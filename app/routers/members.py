from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/workspaces/{workspace_id}/members", tags=["members"])


@router.post("", response_model=schemas.MemberOut)
def create_member(workspace_id: int, payload: schemas.MemberCreate, db: Session = Depends(get_db)):
    workspace = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    member = models.Member(workspace_id=workspace_id, **payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("", response_model=list[schemas.MemberOut])
def list_members(workspace_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Member)
        .filter(models.Member.workspace_id == workspace_id)
        .order_by(models.Member.created_at.desc())
        .all()
    )
