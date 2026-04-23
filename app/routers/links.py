from fastapi import APIRouter, Depends, HTTPException

from .. import schemas
from ..database import DESC, MongoStore, get_db
from ..rbac import require_workspace_permission

router = APIRouter(prefix="/workspaces/{workspace_id}/links", tags=["links"])


@router.post("", response_model=schemas.LinkOut)
def create_link(
    workspace_id: int,
    payload: schemas.LinkCreate,
    db: MongoStore = Depends(get_db),
    _membership=Depends(require_workspace_permission("settings.edit")),
):
    if not db.find_by_id("workspaces", workspace_id):
        raise HTTPException(status_code=404, detail="Workspace not found")
    if db.find_one("short_links", {"slug": payload.slug}):
        raise HTTPException(status_code=409, detail="Short link slug already exists")

    return db.insert("short_links", {"workspace_id": workspace_id, "click_count": 0, "is_active": True, **payload.model_dump()})


@router.get("", response_model=list[schemas.LinkOut])
def list_links(workspace_id: int, db: MongoStore = Depends(get_db)):
    return db.find_many("short_links", {"workspace_id": workspace_id}, sort=[("created_at", DESC)])
