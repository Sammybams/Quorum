from fastapi import APIRouter, Depends, HTTPException

from .. import models, schemas
from ..database import DESC, MongoStore, get_db
from ..membership import role_key_from_input, sync_workspace_members_from_legacy
from ..rbac import ensure_default_roles, require_workspace_permission

router = APIRouter(prefix="/workspaces/{workspace_id}/members", tags=["members"])


@router.post("", response_model=schemas.WorkspaceMemberOut)
def create_member(
    workspace_id: int,
    payload: schemas.MemberCreate,
    db: MongoStore = Depends(get_db),
    _membership=Depends(require_workspace_permission("members.invite")),
):
    workspace = db.find_by_id("workspaces", workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    roles = ensure_default_roles(db, workspace_id)
    role_key = role_key_from_input(payload.role)
    role = roles.get(role_key) or roles["core_member"]
    email = payload.email.strip().lower()

    user = db.find_one("users", {"email": email})
    if user is None:
        user = db.insert(
            "users",
            {"full_name": payload.full_name.strip(), "email": email, "phone": None, "password_hash": None, "email_verified": False},
        )

    if db.find_one("workspace_members", {"workspace_id": workspace_id, "user_id": user.id}):
        raise HTTPException(status_code=409, detail="Member already belongs to this workspace")

    membership = db.insert(
        "workspace_members",
        {
            "workspace_id": workspace_id,
            "user_id": user.id,
            "role_id": role.id,
            "level": payload.level,
            "dues_status": "defaulter",
            "is_general_member": role.key == "core_member",
            "status": "active",
            "joined_at": user.created_at,
        },
    )

    db.insert(
        "members",
        {
            "workspace_id": workspace_id,
            "full_name": user.full_name,
            "email": user.email,
            "role": role.name,
            "level": payload.level,
            "dues_status": "defaulter",
        },
    )
    return _member_out(db, membership)


@router.get("", response_model=list[schemas.WorkspaceMemberOut])
def list_members(workspace_id: int, db: MongoStore = Depends(get_db)):
    workspace = db.find_by_id("workspaces", workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    sync_workspace_members_from_legacy(db, workspace)
    memberships = db.find_many("workspace_members", {"workspace_id": workspace_id}, sort=[("joined_at", DESC), ("created_at", DESC)])
    return [_member_out(db, membership) for membership in memberships]


def _member_out(db: MongoStore, membership: models.WorkspaceMember) -> schemas.WorkspaceMemberOut:
    user = db.find_by_id("users", membership.user_id)
    role = db.find_by_id("roles", membership.role_id)
    return schemas.WorkspaceMemberOut(
        id=membership.id,
        workspace_id=membership.workspace_id,
        user_id=membership.user_id,
        role_id=membership.role_id,
        full_name=user.full_name,
        email=user.email,
        role=role.name,
        role_key=role.key,
        level=membership.get("level"),
        dues_status=membership.get("dues_status", "defaulter"),
        status=membership.get("status", "active"),
        is_general_member=membership.get("is_general_member", False),
        created_at=membership.get("joined_at") or membership.created_at,
    )
