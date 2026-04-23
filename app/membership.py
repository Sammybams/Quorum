from sqlalchemy.orm import Session

from . import models
from .rbac import ensure_default_roles


def sync_workspace_members_from_legacy(db: Session, workspace: models.Workspace) -> None:
    roles = ensure_default_roles(db, workspace.id)
    changed = False
    legacy_members = db.query(models.Member).filter(models.Member.workspace_id == workspace.id).all()

    for legacy_member in legacy_members:
        email = legacy_member.email.strip().lower()
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            user = models.User(
                full_name=legacy_member.full_name,
                email=email,
                phone=None,
                password_hash=None,
                email_verified=False,
            )
            db.add(user)
            db.flush()
            changed = True

        membership = (
            db.query(models.WorkspaceMember)
            .filter(models.WorkspaceMember.workspace_id == workspace.id, models.WorkspaceMember.user_id == user.id)
            .first()
        )
        if membership is None:
            role_key = role_key_from_input(legacy_member.role)
            membership = models.WorkspaceMember(
                workspace_id=workspace.id,
                user_id=user.id,
                role_id=roles[role_key].id,
                level=legacy_member.level,
                dues_status=legacy_member.dues_status,
                is_general_member=role_key == "core_member",
                status="active",
            )
            db.add(membership)
            changed = True

    if changed:
        db.commit()


def role_key_from_input(role: str | None) -> str:
    normalized = (role or "").strip().lower().replace(" ", "_")
    if normalized in {"owner", "president", "lead", "super_admin", "workspace_owner"}:
        return "owner"
    if normalized in {"secretary", "general_secretary", "scribe"}:
        return "secretary"
    return "core_member"
