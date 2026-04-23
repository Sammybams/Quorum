from fastapi import APIRouter, Depends, HTTPException

from .. import schemas
from ..database import DESC, MongoStore, get_db
from ..membership import sync_workspace_members_from_legacy
from ..rbac import require_workspace_permission

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=schemas.WorkspaceOut)
def create_workspace(payload: schemas.WorkspaceCreate, db: MongoStore = Depends(get_db)):
    if db.find_one("workspaces", {"slug": payload.slug}):
        raise HTTPException(status_code=409, detail="Workspace slug already exists")
    return db.insert("workspaces", payload.model_dump())


@router.get("", response_model=list[schemas.WorkspaceOut])
def list_workspaces(db: MongoStore = Depends(get_db)):
    return db.find_many("workspaces", sort=[("created_at", DESC)])


@router.get("/slug/{slug}", response_model=schemas.WorkspaceOut)
def get_workspace_by_slug(slug: str, db: MongoStore = Depends(get_db)):
    workspace = db.find_one("workspaces", {"slug": slug})
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.get("/slug/{slug}/overview", response_model=schemas.WorkspaceOverview)
def get_workspace_overview(slug: str, db: MongoStore = Depends(get_db)):
    workspace = db.find_one("workspaces", {"slug": slug})
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    sync_workspace_members_from_legacy(db, workspace)

    active_filter = {"workspace_id": workspace.id, "status": "active"}
    member_count = db.count("workspace_members", active_filter)
    paid_members = db.count("workspace_members", {**active_filter, "dues_status": "paid"})

    return schemas.WorkspaceOverview(
        workspace=workspace,
        counts=schemas.DashboardCounts(
            members=member_count,
            dues_cycles=db.count("dues_cycles", {"workspace_id": workspace.id}),
            events=db.count("events", {"workspace_id": workspace.id}),
            campaigns=db.count("campaigns", {"workspace_id": workspace.id}),
            links=db.count("short_links", {"workspace_id": workspace.id}),
            paid_members=paid_members,
            pending_members=max(member_count - paid_members, 0),
        ),
        recent_events=db.find_many("events", {"workspace_id": workspace.id}, sort=[("created_at", DESC)], limit=4),
        active_campaigns=db.find_many("campaigns", {"workspace_id": workspace.id}, sort=[("created_at", DESC)], limit=4),
        dues_cycles=db.find_many("dues_cycles", {"workspace_id": workspace.id}, sort=[("created_at", DESC)], limit=4),
        links=db.find_many("short_links", {"workspace_id": workspace.id}, sort=[("created_at", DESC)], limit=4),
        announcements=db.find_many(
            "announcements",
            {"workspace_id": workspace.id, "status": "published"},
            sort=[("is_pinned", DESC), ("published_at", DESC)],
            limit=4,
        ),
    )


@router.get("/{workspace_id}", response_model=schemas.WorkspaceOut)
def get_workspace(workspace_id: int, db: MongoStore = Depends(get_db)):
    workspace = db.find_by_id("workspaces", workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.patch("/{workspace_id}", response_model=schemas.WorkspaceOut)
def update_workspace(
    workspace_id: int,
    payload: schemas.WorkspaceUpdate,
    db: MongoStore = Depends(get_db),
    _membership=Depends(require_workspace_permission("settings.edit")),
):
    workspace = db.find_by_id("workspaces", workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    values = payload.model_dump(exclude_unset=True)
    if values.get("slug") and values["slug"] != workspace.slug:
        if db.find_one("workspaces", {"slug": values["slug"]}):
            raise HTTPException(status_code=409, detail="Workspace slug already exists")
        workspace["slug"] = values["slug"].strip().lower()
    if "name" in values and values["name"] is not None:
        workspace["name"] = values["name"].strip()
    if "description" in values:
        workspace["description"] = values["description"]

    return db.save("workspaces", workspace)
