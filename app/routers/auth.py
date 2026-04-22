from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_response(workspace: models.Workspace, member: models.Member) -> schemas.AuthLoginResponse:
    return schemas.AuthLoginResponse(
        workspace_slug=workspace.slug,
        workspace_name=workspace.name,
        member_id=member.id,
        member_name=member.full_name,
        member_role=member.role,
    )


@router.post("/register", response_model=schemas.AuthLoginResponse, status_code=201)
def register(payload: schemas.AuthRegisterRequest, db: Session = Depends(get_db)):
    workspace_slug = payload.workspace_slug.strip().lower()
    admin_email = payload.admin_email.strip().lower()

    existing_workspace = db.query(models.Workspace).filter(models.Workspace.slug == workspace_slug).first()
    if existing_workspace:
        raise HTTPException(status_code=409, detail="Workspace slug already exists")

    existing_member = db.query(models.Member).filter(models.Member.email == admin_email).first()
    if existing_member:
        raise HTTPException(status_code=409, detail="This email already belongs to a workspace")

    description_parts = [payload.university, payload.body_type, payload.faculty]
    description = " · ".join([part.strip() for part in description_parts if part and part.strip()]) or None

    workspace = models.Workspace(
        name=payload.organization_name.strip(),
        slug=workspace_slug,
        description=description,
    )
    db.add(workspace)
    db.flush()

    member = models.Member(
        workspace_id=workspace.id,
        full_name=payload.admin_name.strip(),
        email=admin_email,
        role=payload.admin_role,
        level="Admin",
        dues_status="paid",
    )
    db.add(member)
    db.commit()
    db.refresh(workspace)
    db.refresh(member)
    return _auth_response(workspace, member)


@router.post("/login", response_model=schemas.AuthLoginResponse)
def login(payload: schemas.AuthLoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    workspace = None

    query = db.query(models.Member).filter(models.Member.email == email)
    if payload.workspace_slug:
        workspace = db.query(models.Workspace).filter(models.Workspace.slug == payload.workspace_slug.strip().lower()).first()
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        query = query.filter(models.Member.workspace_id == workspace.id)

    matches = query.all()

    if not matches:
        raise HTTPException(status_code=401, detail="Invalid login details")

    if len(matches) > 1 and not workspace:
        raise HTTPException(status_code=409, detail="Multiple workspaces found for this email. Enter your workspace slug.")

    member = matches[0]
    if workspace is None:
        workspace = db.query(models.Workspace).filter(models.Workspace.id == member.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return _auth_response(workspace, member)
