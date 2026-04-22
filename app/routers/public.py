from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

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
    return {
        "name": campaign.name,
        "slug": campaign.slug,
        "target_amount": campaign.target_amount,
        "raised_amount": campaign.raised_amount,
        "status": campaign.status,
    }


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

    return {
        "workspace": {
            "name": workspace.name,
            "slug": workspace.slug,
            "description": workspace.description,
        },
        "links": [{"slug": l.slug, "destination_url": l.destination_url, "click_count": l.click_count} for l in links],
        "events": [{"title": e.title, "slug": e.slug, "starts_at": e.starts_at, "venue": e.venue} for e in events],
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
