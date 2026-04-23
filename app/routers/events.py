from fastapi import APIRouter, Depends, HTTPException

from .. import schemas
from ..database import DESC, MongoStore, get_db
from ..rbac import require_workspace_permission

router = APIRouter(prefix="/workspaces/{workspace_id}/events", tags=["events"])


@router.post("", response_model=schemas.EventOut)
def create_event(
    workspace_id: int,
    payload: schemas.EventCreate,
    db: MongoStore = Depends(get_db),
    _membership=Depends(require_workspace_permission("events.manage")),
):
    if not db.find_by_id("workspaces", workspace_id):
        raise HTTPException(status_code=404, detail="Workspace not found")
    if db.find_one("events", {"slug": payload.slug}):
        raise HTTPException(status_code=409, detail="Event slug already exists")

    return db.insert("events", {"workspace_id": workspace_id, "rsvp_count": 0, **payload.model_dump()})


@router.get("", response_model=list[schemas.EventOut])
def list_events(workspace_id: int, db: MongoStore = Depends(get_db)):
    return db.find_many("events", {"workspace_id": workspace_id}, sort=[("created_at", DESC)])
