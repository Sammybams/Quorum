from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from .. import schemas
from ..database import DESC, MongoStore, get_db
from ..payments import PaymentInitializationError, initialize_paystack_transaction, payment_callback_url
from .campaigns import _contribution_out, _stream_out

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/e/{event_slug}")
def get_public_event(event_slug: str, db: MongoStore = Depends(get_db)):
    event = db.find_one("events", {"slug": event_slug})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {
        "title": event.title,
        "slug": event.slug,
        "event_type": event.event_type,
        "starts_at": event.starts_at,
        "venue": event.get("venue"),
        "description": event.get("description"),
        "rsvp_enabled": event.get("rsvp_enabled", True),
        "rsvp_count": event.get("rsvp_count", 0),
    }


@router.get("/donate/{campaign_slug}")
def get_public_campaign(campaign_slug: str, db: MongoStore = Depends(get_db)):
    campaign = db.find_one("campaigns", {"slug": campaign_slug})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    workspace = db.find_by_id("workspaces", campaign.workspace_id)
    streams = db.find_many("funding_streams", {"campaign_id": campaign.id})
    contributions = db.find_many("contributions", {"campaign_id": campaign.id, "status": "confirmed"})
    confirmed_contributors = {
        contribution.get("contributor_email") or contribution.get("contributor_name") or str(contribution.id)
        for contribution in contributions
    }
    return {
        "name": campaign.name,
        "slug": campaign.slug,
        "target_amount": campaign.target_amount,
        "raised_amount": campaign.get("raised_amount", 0),
        "status": campaign.status,
        "workspace": {"name": workspace.name, "slug": workspace.slug},
        "funding_streams": [_stream_out(db, stream).model_dump() for stream in streams],
        "contributor_count": len(confirmed_contributors),
    }


@router.post("/donate/{campaign_slug}/submissions", response_model=schemas.PublicContributionResponse)
def submit_public_contribution(
    campaign_slug: str,
    payload: schemas.PublicContributionCreate,
    db: MongoStore = Depends(get_db),
):
    campaign = db.find_one("campaigns", {"slug": campaign_slug})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status != "active":
        raise HTTPException(status_code=400, detail="Campaign is not accepting contributions")

    if payload.stream_id:
        stream = db.find_one(
            "funding_streams",
            {"id": payload.stream_id, "campaign_id": campaign.id, "workspace_id": campaign.workspace_id},
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

    contribution = db.insert(
        "contributions",
        {
            "workspace_id": campaign.workspace_id,
            "campaign_id": campaign.id,
            "stream_id": payload.stream_id,
            "contributor_name": payload.contributor_name,
            "contributor_email": payload.contributor_email,
            "amount": payload.amount,
            "method": "paystack" if checkout else "public",
            "gateway_ref": reference,
            "receipt_url": None,
            "is_anonymous": payload.is_anonymous,
            "status": "pending",
            "confirmed_by_user_id": None,
            "confirmed_at": None,
        },
    )

    return schemas.PublicContributionResponse(
        contribution=_contribution_out(db, contribution),
        payment_reference=reference,
        checkout_url=checkout.authorization_url if checkout else None,
        access_code=checkout.access_code if checkout else None,
    )


@router.get("/portal/{workspace_slug}")
def get_public_portal(workspace_slug: str, db: MongoStore = Depends(get_db)):
    workspace = db.find_one("workspaces", {"slug": workspace_slug})
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    links = db.find_many("short_links", {"workspace_id": workspace.id, "is_active": True}, sort=[("created_at", DESC)])
    events = db.find_many("events", {"workspace_id": workspace.id}, sort=[("created_at", DESC)], limit=5)
    announcements = db.find_many(
        "announcements",
        {"workspace_id": workspace.id, "status": "published"},
        sort=[("is_pinned", DESC), ("published_at", DESC)],
        limit=5,
    )

    return {
        "workspace": {"name": workspace.name, "slug": workspace.slug, "description": workspace.get("description")},
        "links": [{"slug": item.slug, "destination_url": item.destination_url, "click_count": item.get("click_count", 0)} for item in links],
        "events": [{"title": item.title, "slug": item.slug, "starts_at": item.starts_at, "venue": item.get("venue")} for item in events],
        "announcements": [
            {"title": item.title, "body": item.body, "is_pinned": item.get("is_pinned", False), "published_at": item.get("published_at")}
            for item in announcements
        ],
    }


@router.get("/r/{slug}")
def resolve_short_link(slug: str, db: MongoStore = Depends(get_db)):
    short_link = db.find_one("short_links", {"slug": slug, "is_active": True})
    if not short_link:
        raise HTTPException(status_code=404, detail="Short link not found")
    db.increment("short_links", {"id": short_link.id}, "click_count", 1)
    short_link["click_count"] = short_link.get("click_count", 0) + 1
    return {"destination_url": short_link.destination_url, "click_count": short_link.click_count}
