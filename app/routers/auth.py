from fastapi import APIRouter, Depends, HTTPException

from .. import models, schemas
from ..database import MongoStore, get_db
from ..membership import sync_workspace_members_from_legacy
from ..rbac import ensure_default_roles, get_current_user, hydrate_user
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_response(db: MongoStore, workspace: models.Workspace, membership: models.WorkspaceMember) -> schemas.AuthLoginResponse:
    user = db.find_by_id("users", membership.user_id)
    role = db.find_by_id("roles", membership.role_id)
    hydrate_user(db, user)
    token = create_access_token(str(membership.user_id), {"workspace_id": workspace.id, "member_id": membership.id, "role": role.key})
    return schemas.AuthLoginResponse(
        workspace_slug=workspace.slug,
        workspace_name=workspace.name,
        member_id=membership.id,
        member_name=user.full_name,
        member_role=role.name,
        user_id=membership.user_id,
        role_key=role.key,
        access_token=token,
        workspaces=[_workspace_member_out(item) for item in user.workspace_memberships],
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
def register(payload: schemas.AuthRegisterRequest, db: MongoStore = Depends(get_db)):
    workspace_slug = payload.workspace_slug.strip().lower()
    admin_email = payload.admin_email.strip().lower()

    if db.find_one("workspaces", {"slug": workspace_slug}):
        raise HTTPException(status_code=409, detail="Workspace slug already exists")
    if db.find_one("users", {"email": admin_email}):
        raise HTTPException(status_code=409, detail="This email already belongs to an account")

    description_parts = [payload.university, payload.body_type, payload.faculty]
    description = " · ".join([part.strip() for part in description_parts if part and part.strip()]) or None

    user = db.insert(
        "users",
        {
            "full_name": payload.admin_name.strip(),
            "email": admin_email,
            "phone": payload.phone_number.strip() if payload.phone_number else None,
            "password_hash": hash_password(payload.password or ""),
            "email_verified": False,
        },
    )
    workspace = db.insert(
        "workspaces",
        {"name": payload.organization_name.strip(), "slug": workspace_slug, "description": description},
    )

    roles = ensure_default_roles(db, workspace.id)
    owner_role = roles["owner"]
    if payload.admin_role:
        owner_role["name"] = payload.admin_role.replace("_", " ").title()
        db.save("roles", owner_role)

    membership = db.insert(
        "workspace_members",
        {
            "workspace_id": workspace.id,
            "user_id": user.id,
            "role_id": owner_role.id,
            "level": "Admin",
            "dues_status": "paid",
            "is_general_member": False,
            "status": "active",
        },
    )

    db.insert(
        "members",
        {
            "workspace_id": workspace.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": payload.admin_role or "owner",
            "level": "Admin",
            "dues_status": "paid",
        },
    )

    return _auth_response(db, workspace, membership)


@router.post("/login", response_model=schemas.AuthLoginResponse)
def login(payload: schemas.AuthLoginRequest, db: MongoStore = Depends(get_db)):
    email = payload.email.strip().lower()
    workspace_slug = payload.workspace_slug.strip().lower() if payload.workspace_slug else None

    user = db.find_one("users", {"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login details")

    password = payload.password or ""
    if user.get("password_hash"):
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid login details")
    else:
        if not password:
            raise HTTPException(status_code=401, detail="Password is required")
        user["password_hash"] = hash_password(password)
        db.save("users", user)

    for workspace in db.find_many("workspaces"):
        ensure_default_roles(db, workspace.id)
        sync_workspace_members_from_legacy(db, workspace)

    memberships = db.find_many("workspace_members", {"user_id": user.id, "status": "active"})
    for membership in memberships:
        membership.workspace = db.find_by_id("workspaces", membership.workspace_id)
        membership.role = db.find_by_id("roles", membership.role_id)
    if workspace_slug:
        memberships = [membership for membership in memberships if membership.workspace and membership.workspace.slug == workspace_slug]
    memberships = sorted(memberships, key=lambda item: item.workspace.name if item.workspace else "")

    if not memberships:
        raise HTTPException(status_code=401, detail="No active workspace membership found")

    if workspace_slug or len(memberships) == 1:
        membership = memberships[0]
        return _auth_response(db, membership.workspace, membership)

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
    return schemas.AuthMeResponse(
        user=user,
        workspaces=[_workspace_member_out(membership) for membership in user.workspace_memberships],
    )
