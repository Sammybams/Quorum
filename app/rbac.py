from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .security import decode_access_token


OWNER_PERMISSIONS = [
    "dashboard.view",
    "members.view",
    "members.invite",
    "members.edit",
    "members.remove",
    "dues.view",
    "dues.manage",
    "dues.confirm_payment",
    "events.view",
    "events.manage",
    "events.attendance",
    "meetings.view",
    "meetings.manage",
    "meetings.publish_minutes",
    "tasks.view",
    "tasks.assign",
    "tasks.manage_all",
    "campaigns.view",
    "campaigns.manage",
    "campaigns.confirm_contribution",
    "budgets.view",
    "budgets.manage",
    "announcements.view",
    "announcements.publish",
    "settings.view",
    "settings.edit",
    "roles.manage",
    "billing.manage",
    "integrations.manage",
    "ownership.transfer",
]

SECRETARY_PERMISSIONS = [
    "dashboard.view",
    "members.view",
    "members.invite",
    "dues.view",
    "events.view",
    "meetings.view",
    "meetings.manage",
    "meetings.publish_minutes",
    "tasks.view",
    "tasks.assign",
    "campaigns.view",
    "budgets.view",
    "announcements.view",
    "announcements.publish",
    "settings.view",
]

CORE_MEMBER_PERMISSIONS = [
    "dashboard.view",
    "members.view",
    "dues.view",
    "events.view",
    "meetings.view",
    "tasks.view",
    "campaigns.view",
    "announcements.view",
]


DEFAULT_ROLE_DEFINITIONS = [
    ("owner", "Workspace Owner", "System owner role with full access.", OWNER_PERMISSIONS, True),
    ("secretary", "Secretary", "System secretary role for meetings, minutes, and announcements.", SECRETARY_PERMISSIONS, True),
    ("core_member", "Core Member", "General member role with personal read access.", CORE_MEMBER_PERMISSIONS, False),
]


def ensure_default_roles(db: Session, workspace_id: int) -> dict[str, models.Role]:
    roles: dict[str, models.Role] = {}
    for key, name, description, permissions, is_system_role in DEFAULT_ROLE_DEFINITIONS:
        role = (
            db.query(models.Role)
            .filter(models.Role.workspace_id == workspace_id, models.Role.key == key)
            .first()
        )
        if role is None:
            role = models.Role(
                workspace_id=workspace_id,
                key=key,
                name=name,
                description=description,
                is_system_role=is_system_role,
            )
            role.set_permissions(permissions)
            db.add(role)
            db.flush()
        roles[key] = role
    return roles


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> models.User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing access token")

    payload = decode_access_token(authorization.split(" ", 1)[1])
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    user = db.query(models.User).filter(models.User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_workspace_permission(permission: str):
    def dependency(
        workspace_id: int,
        user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> models.WorkspaceMember:
        membership = (
            db.query(models.WorkspaceMember)
            .join(models.Role, models.WorkspaceMember.role_id == models.Role.id)
            .filter(
                models.WorkspaceMember.workspace_id == workspace_id,
                models.WorkspaceMember.user_id == user.id,
                models.WorkspaceMember.status == "active",
            )
            .first()
        )
        if not membership or not membership.role or permission not in membership.role.permissions:
            raise HTTPException(status_code=403, detail="Insufficient permission")
        return membership

    return dependency
