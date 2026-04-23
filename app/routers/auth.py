from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..membership import sync_workspace_members_from_legacy
from ..rbac import ensure_default_roles, get_current_user
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_response(workspace: models.Workspace, membership: models.WorkspaceMember) -> schemas.AuthLoginResponse:
    token = create_access_token(
        str(membership.user_id),
        {"workspace_id": workspace.id, "member_id": membership.id, "role": membership.role.key},
    )
    return schemas.AuthLoginResponse(
        workspace_slug=workspace.slug,
        workspace_name=workspace.name,
        member_id=membership.id,
        member_name=membership.user.full_name,
        member_role=membership.role.name,
        user_id=membership.user_id,
        role_key=membership.role.key,
        access_token=token,
        workspaces=[_workspace_member_out(item) for item in membership.user.workspace_memberships if item.status == "active"],
    )


def _workspace_member_out(membership: models.WorkspaceMember) -> schemas.AuthMeWorkspace:
    return schemas.AuthMeWorkspace(
        workspace_slug=membership.workspace.slug,
        workspace_name=membership.workspace.name,
        member_id=membership.id,
        role=membership.role.name,
        role_key=membership.role.key,
        permissions=membership.role.permissions,
    )


@router.post("/register", response_model=schemas.AuthLoginResponse, status_code=201)
def register(payload: schemas.AuthRegisterRequest, db: Session = Depends(get_db)):
    workspace_slug = payload.workspace_slug.strip().lower()
    admin_email = payload.admin_email.strip().lower()

    existing_workspace = db.query(models.Workspace).filter(models.Workspace.slug == workspace_slug).first()
    if existing_workspace:
        raise HTTPException(status_code=409, detail="Workspace slug already exists")

    existing_user = db.query(models.User).filter(models.User.email == admin_email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="This email already belongs to an account")

    description_parts = [payload.university, payload.body_type, payload.faculty]
    description = " · ".join([part.strip() for part in description_parts if part and part.strip()]) or None

    user = models.User(
        full_name=payload.admin_name.strip(),
        email=admin_email,
        phone=payload.phone_number.strip() if payload.phone_number else None,
        password_hash=hash_password(payload.password or ""),
        email_verified=False,
    )
    workspace = models.Workspace(
        name=payload.organization_name.strip(),
        slug=workspace_slug,
        description=description,
    )

    db.add(user)
    db.add(workspace)
    db.flush()

    roles = ensure_default_roles(db, workspace.id)
    owner_role = roles["owner"]
    owner_role.name = payload.admin_role.replace("_", " ").title() if payload.admin_role else owner_role.name

    membership = models.WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user.id,
        role_id=owner_role.id,
        level="Admin",
        dues_status="paid",
        is_general_member=False,
        status="active",
    )
    db.add(membership)

    # Temporary compatibility row for existing pages until Member is fully retired.
    legacy_member = models.Member(
        workspace_id=workspace.id,
        full_name=user.full_name,
        email=user.email,
        role=payload.admin_role or "owner",
        level="Admin",
        dues_status="paid",
    )
    db.add(legacy_member)

    db.commit()
    db.refresh(workspace)
    db.refresh(membership)
    return _auth_response(workspace, membership)


@router.post("/login", response_model=schemas.AuthLoginResponse)
def login(payload: schemas.AuthLoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    workspace_slug = payload.workspace_slug.strip().lower() if payload.workspace_slug else None

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login details")

    password = payload.password or ""
    if user.password_hash:
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid login details")
    else:
        if not password:
            raise HTTPException(status_code=401, detail="Password is required")
        user.password_hash = hash_password(password)
        db.commit()
        db.refresh(user)

    for workspace in db.query(models.Workspace).all():
        ensure_default_roles(db, workspace.id)
        sync_workspace_members_from_legacy(db, workspace)

    query = (
        db.query(models.WorkspaceMember)
        .join(models.Workspace, models.WorkspaceMember.workspace_id == models.Workspace.id)
        .filter(models.WorkspaceMember.user_id == user.id, models.WorkspaceMember.status == "active")
    )
    if workspace_slug:
        query = query.filter(models.Workspace.slug == workspace_slug)

    memberships = query.order_by(models.Workspace.name.asc()).all()
    if not memberships:
        raise HTTPException(status_code=401, detail="No active workspace membership found")

    if workspace_slug or len(memberships) == 1:
        membership = memberships[0]
        return _auth_response(membership.workspace, membership)

    token = create_access_token(str(user.id), {"workspace_id": None, "member_id": None, "role": None})
    return schemas.AuthLoginResponse(
        workspace_slug="",
        workspace_name="",
        member_id=0,
        member_name=user.full_name,
        member_role="",
        user_id=user.id,
        role_key=None,
        access_token=token,
        workspaces=[_workspace_member_out(membership) for membership in memberships],
    )


@router.get("/me", response_model=schemas.AuthMeResponse)
def me(user: models.User = Depends(get_current_user)):
    active_memberships = [membership for membership in user.workspace_memberships if membership.status == "active"]
    return schemas.AuthMeResponse(
        user=user,
        workspaces=[_workspace_member_out(membership) for membership in active_memberships],
    )
