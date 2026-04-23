import os
from datetime import datetime
from typing import Any, Iterable

from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient, ReturnDocument


load_dotenv()

MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING") or os.getenv("MONGODB_URL")
MONGODB_DATABASE_PREFIX = os.getenv("MONGODB_DATABASE_PREFIX") or os.getenv("MONGODB_DATABASE", "")

if not MONGODB_CONNECTION_STRING:
    raise RuntimeError("MONGODB_CONNECTION_STRING is required")


class Doc(dict):
    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    @property
    def permissions(self) -> list[str]:
        value = self.get("permissions", [])
        return value if isinstance(value, list) else []

    def set_permissions(self, permissions: list[str]) -> None:
        self["permissions"] = sorted(set(permissions))


def _as_doc(value: dict[str, Any] | None) -> Doc | None:
    if value is None:
        return None
    value.pop("_id", None)
    return Doc(value)


def _as_docs(values: Iterable[dict[str, Any]]) -> list[Doc]:
    return [doc for item in values if (doc := _as_doc(item)) is not None]


def _clean_sparse_unique_fields(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("gateway_ref") is None:
        payload.pop("gateway_ref", None)
    return payload


class MongoStore:
    collection_databases = {
        "workspaces": "communities",
        "members": "communities",
        "users": "identity",
        "roles": "identity",
        "workspace_members": "identity",
        "invitations": "identity",
        "invite_links": "identity",
        "dues_cycles": "finance",
        "dues_payments": "finance",
        "campaigns": "finance",
        "funding_streams": "finance",
        "contributions": "finance",
        "events": "engagement",
        "announcements": "engagement",
        "short_links": "engagement",
        "counters": "platform",
    }

    collection_names = [
        "workspaces",
        "users",
        "roles",
        "workspace_members",
        "invitations",
        "invite_links",
        "members",
        "dues_cycles",
        "dues_payments",
        "events",
        "campaigns",
        "funding_streams",
        "contributions",
        "short_links",
        "announcements",
        "counters",
    ]

    def __init__(self):
        self.client = MongoClient(MONGODB_CONNECTION_STRING)
        self.database_prefix = MONGODB_DATABASE_PREFIX
        self.ensure_indexes()

    def database_name(self, collection_name: str) -> str:
        segment = self.collection_databases.get(collection_name)
        if not segment:
            raise ValueError(f"Unknown collection: {collection_name}")
        return f"{self.database_prefix}_{segment}" if self.database_prefix else segment

    def database(self, segment: str):
        return self.client[f"{self.database_prefix}_{segment}" if self.database_prefix else segment]

    def collection(self, name: str):
        return self.client[self.database_name(name)][name]

    def ensure_indexes(self) -> None:
        self.collection("workspaces").create_index([("slug", ASCENDING)], unique=True)
        self.collection("users").create_index([("email", ASCENDING)], unique=True)
        self.collection("roles").create_index([("workspace_id", ASCENDING), ("key", ASCENDING)], unique=True)
        self.collection("workspace_members").create_index([("workspace_id", ASCENDING), ("user_id", ASCENDING)], unique=True)
        self.collection("invitations").create_index([("token", ASCENDING)], unique=True)
        self.collection("invite_links").create_index([("token", ASCENDING)], unique=True)
        self.collection("events").create_index([("slug", ASCENDING)], unique=True)
        self.collection("campaigns").create_index([("slug", ASCENDING)], unique=True)
        self.collection("contributions").create_index([("gateway_ref", ASCENDING)], unique=True, sparse=True)
        self.collection("dues_payments").create_index([("gateway_ref", ASCENDING)], unique=True, sparse=True)
        self.collection("short_links").create_index([("slug", ASCENDING)], unique=True)

    def next_id(self, collection_name: str) -> int:
        counter = self.collection("counters").find_one_and_update(
            {"_id": collection_name},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return int(counter["seq"])

    def insert(self, collection_name: str, doc: dict[str, Any]) -> Doc:
        payload = dict(doc)
        _clean_sparse_unique_fields(payload)
        payload.setdefault("id", self.next_id(collection_name))
        payload.setdefault("created_at", datetime.utcnow())
        self.collection(collection_name).insert_one(payload)
        return _as_doc(payload)  # type: ignore[return-value]

    def save(self, collection_name: str, doc: dict[str, Any]) -> Doc:
        payload = dict(doc)
        _clean_sparse_unique_fields(payload)
        if "id" not in payload:
            payload["id"] = self.next_id(collection_name)
        self.collection(collection_name).replace_one({"id": payload["id"]}, payload, upsert=True)
        return _as_doc(payload)  # type: ignore[return-value]

    def find_one(self, collection_name: str, filter: dict[str, Any]) -> Doc | None:
        return _as_doc(self.collection(collection_name).find_one(filter))

    def find_by_id(self, collection_name: str, item_id: int | None) -> Doc | None:
        if item_id is None:
            return None
        return self.find_one(collection_name, {"id": item_id})

    def find_many(
        self,
        collection_name: str,
        filter: dict[str, Any] | None = None,
        sort: list[tuple[str, int]] | None = None,
        limit: int = 0,
    ) -> list[Doc]:
        cursor = self.collection(collection_name).find(filter or {})
        if sort:
            cursor = cursor.sort(sort)
        if limit:
            cursor = cursor.limit(limit)
        return _as_docs(cursor)

    def count(self, collection_name: str, filter: dict[str, Any] | None = None) -> int:
        return self.collection(collection_name).count_documents(filter or {})

    def update_one(self, collection_name: str, filter: dict[str, Any], update: dict[str, Any]) -> Doc | None:
        self.collection(collection_name).update_one(filter, {"$set": update})
        return self.find_one(collection_name, filter)

    def increment(self, collection_name: str, filter: dict[str, Any], field: str, amount: float | int) -> Doc | None:
        self.collection(collection_name).update_one(filter, {"$inc": {field: amount}})
        return self.find_one(collection_name, filter)

    def delete_all_collections(self) -> None:
        for name in self.collection_names:
            self.collection(name).delete_many({})


store = MongoStore()


def get_db():
    yield store


ASC = ASCENDING
DESC = DESCENDING
