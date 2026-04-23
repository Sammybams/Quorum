from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from .. import schemas
from ..database import DESC, MongoStore, get_db
from ..rbac import require_workspace_permission

router = APIRouter(prefix="/workspaces/{workspace_id}/announcements", tags=["announcements"])

VALID_STATUSES = {"draft", "scheduled", "published", "archived"}


def _workspace_or_404(db: MongoStore, workspace_id: int):
    workspace = db.find_by_id("workspaces", workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


def _announcement_or_404(db: MongoStore, workspace_id: int, announcement_id: int):
    announcement = db.find_one("announcements", {"id": announcement_id, "workspace_id": workspace_id})
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcement


def _validate_status(status: str) -> str:
    normalized = status.strip().lower()
    if normalized not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid announcement status")
    return normalized


@router.post("", response_model=schemas.AnnouncementOut, status_code=201)
def create_announcement(
    workspace_id: int,
    payload: schemas.AnnouncementCreate,
    db: MongoStore = Depends(get_db),
    _membership=Depends(require_workspace_permission("announcements.publish")),
):
    _workspace_or_404(db, workspace_id)
    status = _validate_status(payload.status)
    now = datetime.utcnow()
    return db.insert(
        "announcements",
        {
            "workspace_id": workspace_id,
            "title": payload.title.strip(),
            "body": payload.body.strip(),
            "status": status,
            "is_pinned": payload.is_pinned,
            "published_at": payload.published_at or (now if status == "published" else None),
            "archived_at": now if status == "archived" else None,
            "updated_at": now,
        },
    )


@router.get("", response_model=list[schemas.AnnouncementOut])
def list_announcements(workspace_id: int, db: MongoStore = Depends(get_db)):
    _workspace_or_404(db, workspace_id)
    return db.find_many("announcements", {"workspace_id": workspace_id}, sort=[("is_pinned", DESC), ("created_at", DESC)])


@router.patch("/{announcement_id}", response_model=schemas.AnnouncementOut)
def update_announcement(
    workspace_id: int,
    announcement_id: int,
    payload: schemas.AnnouncementUpdate,
    db: MongoStore = Depends(get_db),
    _membership=Depends(require_workspace_permission("announcements.publish")),
):
    announcement = _announcement_or_404(db, workspace_id, announcement_id)
    values = payload.model_dump(exclude_unset=True)
    now = datetime.utcnow()

    if "title" in values and values["title"] is not None:
        announcement["title"] = values["title"].strip()
    if "body" in values and values["body"] is not None:
        announcement["body"] = values["body"].strip()
    if "is_pinned" in values and values["is_pinned"] is not None:
        announcement["is_pinned"] = values["is_pinned"]
    if "published_at" in values:
        announcement["published_at"] = values["published_at"]
    if "status" in values and values["status"] is not None:
        status = _validate_status(values["status"])
        announcement["status"] = status
        if status == "published" and announcement.get("published_at") is None:
            announcement["published_at"] = now
        if status == "archived":
            announcement["archived_at"] = now
            announcement["is_pinned"] = False
        elif announcement.get("archived_at") is not None:
            announcement["archived_at"] = None
    announcement["updated_at"] = now
    return db.save("announcements", announcement)
