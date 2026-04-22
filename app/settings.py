import os

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
MONGODB_URL = os.getenv("MONGODB_URL", "")


def is_sqlite_mode() -> bool:
    return DB_ENGINE == "sqlite"


def is_mongodb_mode() -> bool:
    return DB_ENGINE == "mongodb"
