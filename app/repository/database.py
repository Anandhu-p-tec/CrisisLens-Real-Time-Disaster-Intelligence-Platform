from __future__ import annotations

import aiosqlite
import logging
from pathlib import Path

from app.core.config import settings

_logger = logging.getLogger(__name__)

CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS crisis_events (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id           TEXT UNIQUE NOT NULL,
    text              TEXT NOT NULL,
    platform          TEXT NOT NULL,
    created_at        TEXT NOT NULL,
    labels            TEXT NOT NULL,
    severity          REAL NOT NULL,
    confidence        REAL NOT NULL,
    lat               REAL,
    lng               REAL,
    location_raw      TEXT,
    reasoning         TEXT,
    recommended_action TEXT,
    human_override    INTEGER NOT NULL DEFAULT 0,
    indexed_at        TEXT NOT NULL
)
"""


async def get_connection() -> aiosqlite.Connection:
    db_path = Path(settings.DATABASE_URL)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(str(db_path))
    conn.row_factory = aiosqlite.Row
    return conn


async def initialise_database() -> None:
    db_path = Path(settings.DATABASE_URL)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(str(db_path))
    try:
        conn.row_factory = aiosqlite.Row
        await conn.execute(CREATE_EVENTS_TABLE)
        await conn.commit()
        _logger.info("Database initialised at %s", settings.DATABASE_URL)
    finally:
        await conn.close()


