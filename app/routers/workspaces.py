from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..membership import sync_workspace_members_from_legacy
from ..rbac import require_workspace_permission

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=schemas.WorkspaceOut)
def create_workspace(payload: schemas.WorkspaceCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Workspace).filter(models.Workspace.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="Workspace slug already exists")

    workspace = models.Workspace(**payload.model_dump())
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


@router.get("", response_model=list[schemas.WorkspaceOut])
def list_workspaces(db: Session = Depends(get_db)):
    return db.query(models.Workspace).order_by(models.Workspace.created_at.desc()).all()


@router.get("/slug/{slug}", response_model=schemas.WorkspaceOut)
def get_workspace_by_slug(slug: str, db: Session = Depends(get_db)):
    workspace = db.query(models.Workspace).filter(models.Workspace.slug == slug).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.get("/slug/{slug}/overview", response_model=schemas.WorkspaceOverview)
def get_workspace_overview(slug: str, db: Session = Depends(get_db)):
    workspace = db.query(models.Workspace).filter(models.Workspace.slug == slug).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    sync_workspace_members_from_legacy(db, workspace)

    member_count = (
        db.query(func.count(models.WorkspaceMember.id))
        .filter(models.WorkspaceMember.workspace_id == workspace.id, models.WorkspaceMember.status == "active")
        .scalar()
        or 0
    )
    paid_members = (
        db.query(func.count(models.WorkspaceMember.id))
        .filter(
            models.WorkspaceMember.workspace_id == workspace.id,
            models.WorkspaceMember.status == "active",
            func.lower(models.WorkspaceMember.dues_status) == "paid",
        )
        .scalar()
        or 0
    )
    dues_cycle_count = (
        db.query(func.count(models.DuesCycle.id)).filter(models.DuesCycle.workspace_id == workspace.id).scalar() or 0
    )
    event_count = db.query(func.count(models.Event.id)).filter(models.Event.workspace_id == workspace.id).scalar() or 0
    campaign_count = (
        db.query(func.count(models.Campaign.id)).filter(models.Campaign.workspace_id == workspace.id).scalar() or 0
    )
    link_count = db.query(func.count(models.ShortLink.id)).filter(models.ShortLink.workspace_id == workspace.id).scalar() or 0

    recent_events = (
        db.query(models.Event)
        .filter(models.Event.workspace_id == workspace.id)
        .order_by(models.Event.created_at.desc())
        .limit(4)
        .all()
    )
    active_campaigns = (
        db.query(models.Campaign)
        .filter(models.Campaign.workspace_id == workspace.id)
        .order_by(models.Campaign.created_at.desc())
        .limit(4)
        .all()
    )
    dues_cycles = (
        db.query(models.DuesCycle)
        .filter(models.DuesCycle.workspace_id == workspace.id)
        .order_by(models.DuesCycle.created_at.desc())
        .limit(4)
        .all()
    )
    links = (
        db.query(models.ShortLink)
        .filter(models.ShortLink.workspace_id == workspace.id)
        .order_by(models.ShortLink.created_at.desc())
        .limit(4)
        .all()
    )

    return schemas.WorkspaceOverview(
        workspace=workspace,
        counts=schemas.DashboardCounts(
            members=member_count,
            dues_cycles=dues_cycle_count,
            events=event_count,
            campaigns=campaign_count,
            links=link_count,
            paid_members=paid_members,
            pending_members=max(member_count - paid_members, 0),
        ),
        recent_events=recent_events,
        active_campaigns=active_campaigns,
        dues_cycles=dues_cycles,
        links=links,
    )


@router.get("/{workspace_id}", response_model=schemas.WorkspaceOut)
def get_workspace(workspace_id: int, db: Session = Depends(get_db)):
    workspace = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.patch("/{workspace_id}", response_model=schemas.WorkspaceOut)
def update_workspace(
    workspace_id: int,
    payload: schemas.WorkspaceUpdate,
    db: Session = Depends(get_db),
    _membership: models.WorkspaceMember = Depends(require_workspace_permission("settings.edit")),
):
    workspace = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if payload.slug and payload.slug != workspace.slug:
        existing = db.query(models.Workspace).filter(models.Workspace.slug == payload.slug).first()
        if existing:
            raise HTTPException(status_code=409, detail="Workspace slug already exists")
        workspace.slug = payload.slug.strip().lower()
    if payload.name is not None:
        workspace.name = payload.name.strip()
    if payload.description is not None:
        workspace.description = payload.description

    db.commit()
    db.refresh(workspace)
    return workspace
