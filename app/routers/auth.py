from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.AuthLoginResponse)
def login(payload: schemas.AuthLoginRequest, db: Session = Depends(get_db)):
    workspace = db.query(models.Workspace).filter(models.Workspace.slug == payload.workspace_slug).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    member = (
        db.query(models.Member)
        .filter(models.Member.workspace_id == workspace.id, models.Member.email == payload.email)
        .first()
    )

    if not member:
        raise HTTPException(status_code=401, detail="Invalid login details")

    return schemas.AuthLoginResponse(
        workspace_slug=workspace.slug,
        workspace_name=workspace.name,
        member_id=member.id,
        member_name=member.full_name,
        member_role=member.role,
    )
