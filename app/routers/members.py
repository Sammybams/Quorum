from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..membership import role_key_from_input, sync_workspace_members_from_legacy
from ..rbac import ensure_default_roles, require_workspace_permission

router = APIRouter(prefix="/workspaces/{workspace_id}/members", tags=["members"])


@router.post("", response_model=schemas.WorkspaceMemberOut)
def create_member(
    workspace_id: int,
    payload: schemas.MemberCreate,
    db: Session = Depends(get_db),
    _membership: models.WorkspaceMember = Depends(require_workspace_permission("members.invite")),
):
    workspace = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    roles = ensure_default_roles(db, workspace_id)
    role_key = role_key_from_input(payload.role)
    role = roles.get(role_key) or roles["core_member"]
    email = payload.email.strip().lower()

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        user = models.User(
            full_name=payload.full_name.strip(),
            email=email,
            phone=None,
            password_hash=None,
            email_verified=False,
        )
        db.add(user)
        db.flush()

    existing_membership = (
        db.query(models.WorkspaceMember)
        .filter(models.WorkspaceMember.workspace_id == workspace_id, models.WorkspaceMember.user_id == user.id)
        .first()
    )
    if existing_membership:
        raise HTTPException(status_code=409, detail="Member already belongs to this workspace")

    membership = models.WorkspaceMember(
        workspace_id=workspace_id,
        user_id=user.id,
        role_id=role.id,
        level=payload.level,
        dues_status="defaulter",
        is_general_member=role.key == "core_member",
        status="active",
    )
    db.add(membership)

    legacy_member = models.Member(
        workspace_id=workspace_id,
        full_name=user.full_name,
        email=user.email,
        role=role.name,
        level=payload.level,
        dues_status="defaulter",
    )
    db.add(legacy_member)
    db.commit()
    db.refresh(membership)
    return _member_out(membership)


@router.get("", response_model=list[schemas.WorkspaceMemberOut])
def list_members(workspace_id: int, db: Session = Depends(get_db)):
    workspace = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    sync_workspace_members_from_legacy(db, workspace)
    memberships = (
        db.query(models.WorkspaceMember)
        .filter(models.WorkspaceMember.workspace_id == workspace_id)
        .order_by(models.WorkspaceMember.joined_at.desc())
        .all()
    )
    return [_member_out(membership) for membership in memberships]


def _member_out(membership: models.WorkspaceMember) -> schemas.WorkspaceMemberOut:
    return schemas.WorkspaceMemberOut(
        id=membership.id,
        workspace_id=membership.workspace_id,
        user_id=membership.user_id,
        role_id=membership.role_id,
        full_name=membership.user.full_name,
        email=membership.user.email,
        role=membership.role.name,
        role_key=membership.role.key,
        level=membership.level,
        dues_status=membership.dues_status,
        status=membership.status,
        is_general_member=membership.is_general_member,
        created_at=membership.joined_at,
    )
