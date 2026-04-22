from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/workspaces/{workspace_id}/campaigns", tags=["campaigns"])


@router.post("", response_model=schemas.CampaignOut)
def create_campaign(workspace_id: int, payload: schemas.CampaignCreate, db: Session = Depends(get_db)):
    workspace = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    existing_slug = db.query(models.Campaign).filter(models.Campaign.slug == payload.slug).first()
    if existing_slug:
        raise HTTPException(status_code=409, detail="Campaign slug already exists")

    campaign = models.Campaign(workspace_id=workspace_id, **payload.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("", response_model=list[schemas.CampaignOut])
def list_campaigns(workspace_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Campaign)
        .filter(models.Campaign.workspace_id == workspace_id)
        .order_by(models.Campaign.created_at.desc())
        .all()
    )
