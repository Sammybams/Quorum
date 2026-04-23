from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..rbac import require_workspace_permission

router = APIRouter(prefix="/workspaces/{workspace_id}/links", tags=["links"])


@router.post("", response_model=schemas.LinkOut)
def create_link(
    workspace_id: int,
    payload: schemas.LinkCreate,
    db: Session = Depends(get_db),
    _membership: models.WorkspaceMember = Depends(require_workspace_permission("settings.edit")),
):
    workspace = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    existing_slug = db.query(models.ShortLink).filter(models.ShortLink.slug == payload.slug).first()
    if existing_slug:
        raise HTTPException(status_code=409, detail="Short link slug already exists")

    short_link = models.ShortLink(workspace_id=workspace_id, **payload.model_dump())
    db.add(short_link)
    db.commit()
    db.refresh(short_link)
    return short_link


@router.get("", response_model=list[schemas.LinkOut])
def list_links(workspace_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.ShortLink)
        .filter(models.ShortLink.workspace_id == workspace_id)
        .order_by(models.ShortLink.created_at.desc())
        .all()
    )
