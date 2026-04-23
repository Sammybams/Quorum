from datetime import datetime, timedelta
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..rbac import require_workspace_permission
from ..security import hash_password
from .auth import _auth_response

router = APIRouter(prefix="/workspaces/{workspace_id}", tags=["invitations"])
public_router = APIRouter(tags=["invitations"])


@router.post("/invitations", response_model=schemas.InvitationOut, status_code=201)
def create_invitation(
    workspace_id: int,
    payload: schemas.InvitationCreate,
    db: Session = Depends(get_db),
    membership: models.WorkspaceMember = Depends(require_workspace_permission("members.invite")),
):
    role = db.query(models.Role).filter(models.Role.workspace_id == workspace_id, models.Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    invitation = models.Invitation(
        workspace_id=workspace_id,
        email=payload.email.strip().lower(),
        role_id=role.id,
        invited_by_user_id=membership.user_id,
        token=secrets.token_urlsafe(32),
        note=payload.note,
        status="pending",
        expires_at=datetime.utcnow() + timedelta(hours=72),
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return _invitation_out(invitation)


@router.get("/invitations", response_model=list[schemas.InvitationOut])
def list_invitations(
    workspace_id: int,
    db: Session = Depends(get_db),
    _membership: models.WorkspaceMember = Depends(require_workspace_permission("members.invite")),
):
    invitations = (
        db.query(models.Invitation)
        .filter(models.Invitation.workspace_id == workspace_id)
        .order_by(models.Invitation.created_at.desc())
        .all()
    )
    return [_invitation_out(invitation) for invitation in invitations]


@router.post("/invite-links", response_model=schemas.InviteLinkOut, status_code=201)
def create_invite_link(
    workspace_id: int,
    payload: schemas.InviteLinkCreate,
    db: Session = Depends(get_db),
    _membership: models.WorkspaceMember = Depends(require_workspace_permission("members.invite")),
):
    role = db.query(models.Role).filter(models.Role.workspace_id == workspace_id, models.Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    link = models.InviteLink(
        workspace_id=workspace_id,
        role_id=role.id,
        token=secrets.token_urlsafe(32),
        is_active=True,
        expires_at=payload.expires_at,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return _invite_link_out(link)


@router.get("/invite-links", response_model=list[schemas.InviteLinkOut])
def list_invite_links(
    workspace_id: int,
    db: Session = Depends(get_db),
    _membership: models.WorkspaceMember = Depends(require_workspace_permission("members.invite")),
):
    links = (
        db.query(models.InviteLink)
        .filter(models.InviteLink.workspace_id == workspace_id)
        .order_by(models.InviteLink.created_at.desc())
        .all()
    )
    return [_invite_link_out(link) for link in links]


@public_router.get("/invites/{token}", response_model=schemas.InvitePreview)
def preview_invitation(token: str, db: Session = Depends(get_db)):
    invitation = db.query(models.Invitation).filter(models.Invitation.token == token).first()
    if not invitation or invitation.status != "pending" or _is_expired(invitation.expires_at):
        raise HTTPException(status_code=404, detail="Invitation not found or expired")
    return schemas.InvitePreview(
        workspace_name=invitation.workspace.name,
        workspace_slug=invitation.workspace.slug,
        email=invitation.email,
        role_name=invitation.role.name,
        expires_at=invitation.expires_at,
    )


@public_router.post("/invites/{token}/accept", response_model=schemas.AuthLoginResponse)
def accept_invitation(token: str, payload: schemas.InvitationAccept, db: Session = Depends(get_db)):
    invitation = db.query(models.Invitation).filter(models.Invitation.token == token).first()
    if not invitation or invitation.status != "pending" or _is_expired(invitation.expires_at):
        raise HTTPException(status_code=404, detail="Invitation not found or expired")

    user = db.query(models.User).filter(models.User.email == invitation.email).first()
    if user is None:
        user = models.User(
            full_name=payload.full_name.strip(),
            email=invitation.email,
            phone=payload.phone_number,
            password_hash=hash_password(payload.password),
            email_verified=False,
        )
        db.add(user)
        db.flush()
    else:
        user.full_name = payload.full_name.strip()
        user.phone = payload.phone_number or user.phone
        user.password_hash = hash_password(payload.password)

    membership = _ensure_membership(db, invitation.workspace, user, invitation.role)
    invitation.status = "accepted"
    invitation.accepted_at = datetime.utcnow()
    db.commit()
    db.refresh(membership)
    return _auth_response(invitation.workspace, membership)


@public_router.get("/join/{token}", response_model=schemas.InvitePreview)
def preview_invite_link(token: str, db: Session = Depends(get_db)):
    link = db.query(models.InviteLink).filter(models.InviteLink.token == token, models.InviteLink.is_active == True).first()
    if not link or _is_expired(link.expires_at):
        raise HTTPException(status_code=404, detail="Invite link not found or expired")
    return schemas.InvitePreview(
        workspace_name=link.workspace.name,
        workspace_slug=link.workspace.slug,
        role_name=link.role.name,
        expires_at=link.expires_at,
    )


@public_router.post("/join/{token}/accept", response_model=schemas.AuthLoginResponse)
def accept_invite_link(token: str, payload: schemas.InviteLinkAccept, db: Session = Depends(get_db)):
    link = db.query(models.InviteLink).filter(models.InviteLink.token == token, models.InviteLink.is_active == True).first()
    if not link or _is_expired(link.expires_at):
        raise HTTPException(status_code=404, detail="Invite link not found or expired")

    email = payload.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        user = models.User(
            full_name=payload.full_name.strip(),
            email=email,
            phone=payload.phone_number,
            password_hash=hash_password(payload.password),
            email_verified=False,
        )
        db.add(user)
        db.flush()
    else:
        user.full_name = payload.full_name.strip()
        user.phone = payload.phone_number or user.phone
        user.password_hash = hash_password(payload.password)

    membership = _ensure_membership(db, link.workspace, user, link.role)
    db.commit()
    db.refresh(membership)
    return _auth_response(link.workspace, membership)


def _invitation_out(invitation: models.Invitation) -> schemas.InvitationOut:
    return schemas.InvitationOut(
        id=invitation.id,
        workspace_id=invitation.workspace_id,
        email=invitation.email,
        role_id=invitation.role_id,
        role_name=invitation.role.name,
        token=invitation.token,
        status=invitation.status,
        expires_at=invitation.expires_at,
        created_at=invitation.created_at,
    )


def _invite_link_out(link: models.InviteLink) -> schemas.InviteLinkOut:
    return schemas.InviteLinkOut(
        id=link.id,
        workspace_id=link.workspace_id,
        role_id=link.role_id,
        role_name=link.role.name,
        token=link.token,
        is_active=link.is_active,
        expires_at=link.expires_at,
        created_at=link.created_at,
    )


def _ensure_membership(
    db: Session,
    workspace: models.Workspace,
    user: models.User,
    role: models.Role,
) -> models.WorkspaceMember:
    membership = (
        db.query(models.WorkspaceMember)
        .filter(models.WorkspaceMember.workspace_id == workspace.id, models.WorkspaceMember.user_id == user.id)
        .first()
    )
    if membership:
        membership.role_id = role.id
        membership.status = "active"
        return membership

    membership = models.WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user.id,
        role_id=role.id,
        is_general_member=role.key == "core_member",
        dues_status="defaulter",
        status="active",
    )
    db.add(membership)
    return membership


def _is_expired(expires_at: datetime | None) -> bool:
    return bool(expires_at and expires_at < datetime.utcnow())
