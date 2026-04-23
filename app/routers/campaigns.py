from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..rbac import require_workspace_permission

router = APIRouter(prefix="/workspaces/{workspace_id}/campaigns", tags=["campaigns"])


def _campaign_or_404(db: Session, workspace_id: int, campaign_id: int) -> models.Campaign:
    campaign = (
        db.query(models.Campaign)
        .filter(models.Campaign.id == campaign_id, models.Campaign.workspace_id == workspace_id)
        .first()
    )
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


def _contribution_out(contribution: models.Contribution) -> schemas.ContributionOut:
    return schemas.ContributionOut(
        id=contribution.id,
        workspace_id=contribution.workspace_id,
        campaign_id=contribution.campaign_id,
        stream_id=contribution.stream_id,
        stream_name=contribution.stream.name if contribution.stream else None,
        contributor_name=None if contribution.is_anonymous else contribution.contributor_name,
        contributor_email=contribution.contributor_email,
        amount=contribution.amount,
        method=contribution.method,
        gateway_ref=contribution.gateway_ref,
        receipt_url=contribution.receipt_url,
        is_anonymous=contribution.is_anonymous,
        status=contribution.status,
        confirmed_by_user_id=contribution.confirmed_by_user_id,
        confirmed_at=contribution.confirmed_at,
        created_at=contribution.created_at,
    )


def _stream_out(stream: models.FundingStream) -> schemas.FundingStreamOut:
    raised_amount = sum(
        contribution.amount for contribution in stream.contributions if contribution.status == "confirmed"
    )
    return schemas.FundingStreamOut(
        id=stream.id,
        workspace_id=stream.workspace_id,
        campaign_id=stream.campaign_id,
        name=stream.name,
        stream_type=stream.stream_type,
        target_amount=stream.target_amount,
        raised_amount=raised_amount,
        created_at=stream.created_at,
    )


def _campaign_detail(campaign: models.Campaign) -> schemas.CampaignDetailOut:
    confirmed_contributors = {
        contribution.contributor_email or contribution.contributor_name or str(contribution.id)
        for contribution in campaign.contributions
        if contribution.status == "confirmed"
    }
    return schemas.CampaignDetailOut(
        id=campaign.id,
        workspace_id=campaign.workspace_id,
        name=campaign.name,
        slug=campaign.slug,
        target_amount=campaign.target_amount,
        raised_amount=campaign.raised_amount,
        status=campaign.status,
        created_at=campaign.created_at,
        funding_streams=[_stream_out(stream) for stream in campaign.funding_streams],
        contributions=[_contribution_out(contribution) for contribution in campaign.contributions],
        contributor_count=len(confirmed_contributors),
    )


def _validate_stream(db: Session, workspace_id: int, campaign_id: int, stream_id: int | None):
    if stream_id is None:
        return None
    stream = (
        db.query(models.FundingStream)
        .filter(
            models.FundingStream.id == stream_id,
            models.FundingStream.workspace_id == workspace_id,
            models.FundingStream.campaign_id == campaign_id,
        )
        .first()
    )
    if not stream:
        raise HTTPException(status_code=404, detail="Funding stream not found")
    return stream


@router.post("", response_model=schemas.CampaignOut)
def create_campaign(
    workspace_id: int,
    payload: schemas.CampaignCreate,
    db: Session = Depends(get_db),
    _membership: models.WorkspaceMember = Depends(require_workspace_permission("campaigns.manage")),
):
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


@router.get("/{campaign_id}", response_model=schemas.CampaignDetailOut)
def get_campaign(workspace_id: int, campaign_id: int, db: Session = Depends(get_db)):
    return _campaign_detail(_campaign_or_404(db, workspace_id, campaign_id))


@router.post("/{campaign_id}/streams", response_model=schemas.FundingStreamOut)
def create_funding_stream(
    workspace_id: int,
    campaign_id: int,
    payload: schemas.FundingStreamCreate,
    db: Session = Depends(get_db),
    _membership: models.WorkspaceMember = Depends(require_workspace_permission("campaigns.manage")),
):
    _campaign_or_404(db, workspace_id, campaign_id)
    stream = models.FundingStream(workspace_id=workspace_id, campaign_id=campaign_id, **payload.model_dump())
    db.add(stream)
    db.commit()
    db.refresh(stream)
    return _stream_out(stream)


@router.get("/{campaign_id}/contributions", response_model=list[schemas.ContributionOut])
def list_contributions(workspace_id: int, campaign_id: int, db: Session = Depends(get_db)):
    _campaign_or_404(db, workspace_id, campaign_id)
    contributions = (
        db.query(models.Contribution)
        .filter(
            models.Contribution.workspace_id == workspace_id,
            models.Contribution.campaign_id == campaign_id,
        )
        .order_by(models.Contribution.created_at.desc())
        .all()
    )
    return [_contribution_out(contribution) for contribution in contributions]


@router.post("/{campaign_id}/contributions/manual", response_model=schemas.ContributionOut)
def create_manual_contribution(
    workspace_id: int,
    campaign_id: int,
    payload: schemas.ContributionCreate,
    db: Session = Depends(get_db),
    membership: models.WorkspaceMember = Depends(require_workspace_permission("campaigns.confirm_contribution")),
):
    campaign = _campaign_or_404(db, workspace_id, campaign_id)
    _validate_stream(db, workspace_id, campaign_id, payload.stream_id)
    if payload.gateway_ref:
        existing = (
            db.query(models.Contribution)
            .filter(models.Contribution.gateway_ref == payload.gateway_ref)
            .first()
        )
        if existing:
            raise HTTPException(status_code=409, detail="Contribution reference already exists")

    contribution = models.Contribution(
        workspace_id=workspace_id,
        campaign_id=campaign_id,
        stream_id=payload.stream_id,
        contributor_name=payload.contributor_name,
        contributor_email=payload.contributor_email,
        amount=payload.amount,
        method=payload.method,
        gateway_ref=payload.gateway_ref,
        receipt_url=payload.receipt_url,
        is_anonymous=payload.is_anonymous,
        status="confirmed",
        confirmed_by_user_id=membership.user_id,
        confirmed_at=datetime.utcnow(),
    )
    campaign.raised_amount += payload.amount
    db.add(contribution)
    db.commit()
    db.refresh(contribution)
    return _contribution_out(contribution)


@router.post("/{campaign_id}/contributions/{contribution_id}/confirm", response_model=schemas.ContributionOut)
def confirm_contribution(
    workspace_id: int,
    campaign_id: int,
    contribution_id: int,
    db: Session = Depends(get_db),
    membership: models.WorkspaceMember = Depends(require_workspace_permission("campaigns.confirm_contribution")),
):
    campaign = _campaign_or_404(db, workspace_id, campaign_id)
    contribution = (
        db.query(models.Contribution)
        .filter(
            models.Contribution.id == contribution_id,
            models.Contribution.workspace_id == workspace_id,
            models.Contribution.campaign_id == campaign_id,
        )
        .first()
    )
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")
    if contribution.status != "confirmed":
        contribution.status = "confirmed"
        contribution.confirmed_by_user_id = membership.user_id
        contribution.confirmed_at = datetime.utcnow()
        campaign.raised_amount += contribution.amount
        db.commit()
        db.refresh(contribution)
    return _contribution_out(contribution)
