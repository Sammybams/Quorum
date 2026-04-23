from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..payments import PaymentInitializationError, initialize_paystack_transaction, payment_callback_url
from .campaigns import _contribution_out, _stream_out

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/e/{event_slug}")
def get_public_event(event_slug: str, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.slug == event_slug).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {
        "title": event.title,
        "slug": event.slug,
        "event_type": event.event_type,
        "starts_at": event.starts_at,
        "venue": event.venue,
        "description": event.description,
        "rsvp_enabled": event.rsvp_enabled,
        "rsvp_count": event.rsvp_count,
    }


@router.get("/donate/{campaign_slug}")
def get_public_campaign(campaign_slug: str, db: Session = Depends(get_db)):
    campaign = db.query(models.Campaign).filter(models.Campaign.slug == campaign_slug).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    confirmed_contributors = {
        contribution.contributor_email or contribution.contributor_name or str(contribution.id)
        for contribution in campaign.contributions
        if contribution.status == "confirmed"
    }
    return {
        "name": campaign.name,
        "slug": campaign.slug,
        "target_amount": campaign.target_amount,
        "raised_amount": campaign.raised_amount,
        "status": campaign.status,
        "workspace": {"name": campaign.workspace.name, "slug": campaign.workspace.slug},
        "funding_streams": [_stream_out(stream).model_dump() for stream in campaign.funding_streams],
        "contributor_count": len(confirmed_contributors),
    }


@router.post("/donate/{campaign_slug}/submissions", response_model=schemas.PublicContributionResponse)
def submit_public_contribution(
    campaign_slug: str,
    payload: schemas.PublicContributionCreate,
    db: Session = Depends(get_db),
):
    campaign = db.query(models.Campaign).filter(models.Campaign.slug == campaign_slug).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status != "active":
        raise HTTPException(status_code=400, detail="Campaign is not accepting contributions")

    if payload.stream_id:
        stream = (
            db.query(models.FundingStream)
            .filter(
                models.FundingStream.id == payload.stream_id,
                models.FundingStream.campaign_id == campaign.id,
                models.FundingStream.workspace_id == campaign.workspace_id,
            )
            .first()
        )
        if not stream:
            raise HTTPException(status_code=404, detail="Funding stream not found")

    reference = f"QRM-CAMP-{uuid4().hex[:14].upper()}"
    checkout = None
    if payload.contributor_email:
        try:
            checkout = initialize_paystack_transaction(
                email=payload.contributor_email,
                amount=payload.amount,
                reference=reference,
                callback_url=payment_callback_url(f"/donate/{campaign.slug}"),
                metadata={
                    "type": "campaign_contribution",
                    "campaign_id": campaign.id,
                    "campaign_slug": campaign.slug,
                    "workspace_id": campaign.workspace_id,
                    "stream_id": payload.stream_id,
                },
            )
        except PaymentInitializationError as exc:
            raise HTTPException(status_code=502, detail=f"Unable to initialize payment: {exc}") from exc

    contribution = models.Contribution(
        workspace_id=campaign.workspace_id,
        campaign_id=campaign.id,
        stream_id=payload.stream_id,
        contributor_name=payload.contributor_name,
        contributor_email=payload.contributor_email,
        amount=payload.amount,
        method="paystack" if checkout else "public",
        gateway_ref=reference,
        is_anonymous=payload.is_anonymous,
        status="pending",
    )
    db.add(contribution)
    db.commit()
    db.refresh(contribution)

    return schemas.PublicContributionResponse(
        contribution=_contribution_out(contribution),
        payment_reference=reference,
        checkout_url=checkout.authorization_url if checkout else None,
        access_code=checkout.access_code if checkout else None,
    )


@router.get("/portal/{workspace_slug}")
def get_public_portal(workspace_slug: str, db: Session = Depends(get_db)):
    workspace = db.query(models.Workspace).filter(models.Workspace.slug == workspace_slug).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    links = (
        db.query(models.ShortLink)
        .filter(models.ShortLink.workspace_id == workspace.id, models.ShortLink.is_active == True)
        .order_by(models.ShortLink.created_at.desc())
        .all()
    )

    events = (
        db.query(models.Event)
        .filter(models.Event.workspace_id == workspace.id)
        .order_by(models.Event.created_at.desc())
        .limit(5)
        .all()
    )

    announcements = (
        db.query(models.Announcement)
        .filter(
            models.Announcement.workspace_id == workspace.id,
            models.Announcement.status == "published",
        )
        .order_by(models.Announcement.is_pinned.desc(), models.Announcement.published_at.desc())
        .limit(5)
        .all()
    )

    return {
        "workspace": {
            "name": workspace.name,
            "slug": workspace.slug,
            "description": workspace.description,
        },
        "links": [{"slug": l.slug, "destination_url": l.destination_url, "click_count": l.click_count} for l in links],
        "events": [{"title": e.title, "slug": e.slug, "starts_at": e.starts_at, "venue": e.venue} for e in events],
        "announcements": [
            {
                "title": announcement.title,
                "body": announcement.body,
                "is_pinned": announcement.is_pinned,
                "published_at": announcement.published_at,
            }
            for announcement in announcements
        ],
    }


@router.get("/r/{slug}")
def resolve_short_link(slug: str, db: Session = Depends(get_db)):
    short_link = (
        db.query(models.ShortLink)
        .filter(models.ShortLink.slug == slug, models.ShortLink.is_active == True)
        .first()
    )
    if not short_link:
        raise HTTPException(status_code=404, detail="Short link not found")

    short_link.click_count += 1
    db.commit()
    db.refresh(short_link)

    return {"destination_url": short_link.destination_url, "click_count": short_link.click_count}
