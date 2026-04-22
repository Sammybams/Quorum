from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

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


@router.get("/{workspace_id}", response_model=schemas.WorkspaceOut)
def get_workspace(workspace_id: int, db: Session = Depends(get_db)):
    workspace = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.get("/slug/{slug}", response_model=schemas.WorkspaceOut)
def get_workspace_by_slug(slug: str, db: Session = Depends(get_db)):
    workspace = db.query(models.Workspace).filter(models.Workspace.slug == slug).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace
