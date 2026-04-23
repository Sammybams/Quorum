from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..rbac import require_workspace_permission

router = APIRouter(prefix="/workspaces/{workspace_id}/events", tags=["events"])


@router.post("", response_model=schemas.EventOut)
def create_event(
    workspace_id: int,
    payload: schemas.EventCreate,
    db: Session = Depends(get_db),
    _membership: models.WorkspaceMember = Depends(require_workspace_permission("events.manage")),
):
    workspace = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    existing_slug = db.query(models.Event).filter(models.Event.slug == payload.slug).first()
    if existing_slug:
        raise HTTPException(status_code=409, detail="Event slug already exists")

    event = models.Event(workspace_id=workspace_id, **payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[schemas.EventOut])
def list_events(workspace_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Event)
        .filter(models.Event.workspace_id == workspace_id)
        .order_by(models.Event.created_at.desc())
        .all()
    )
