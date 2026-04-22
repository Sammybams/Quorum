from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/workspaces/{workspace_id}/dues-cycles", tags=["dues"])


@router.post("", response_model=schemas.DuesCycleOut)
def create_dues_cycle(workspace_id: int, payload: schemas.DuesCycleCreate, db: Session = Depends(get_db)):
    workspace = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    cycle = models.DuesCycle(workspace_id=workspace_id, **payload.model_dump())
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return cycle


@router.get("", response_model=list[schemas.DuesCycleOut])
def list_dues_cycles(workspace_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.DuesCycle)
        .filter(models.DuesCycle.workspace_id == workspace_id)
        .order_by(models.DuesCycle.created_at.desc())
        .all()
    )
