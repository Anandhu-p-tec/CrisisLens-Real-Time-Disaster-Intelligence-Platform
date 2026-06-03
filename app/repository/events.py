from __future__ import annotations

import json
import logging
from datetime import datetime
from datetime import timezone

from app.core.exceptions import StorageError
from app.repository.database import get_connection
from app.repository.schema import CrisisEventRecord

_logger = logging.getLogger(__name__)


async def insert_event(record: CrisisEventRecord) -> int:
    sql = """
    INSERT OR IGNORE INTO crisis_events
    (post_id, text, platform, created_at, labels, severity, confidence,
     lat, lng, location_raw, reasoning, recommended_action, human_override, indexed_at)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    values = (
        record.post_id,
        record.text,
        record.platform,
        record.created_at.isoformat(),
        json.dumps(record.labels),
        record.severity,
        record.confidence,
        record.lat,
        record.lng,
        record.location_raw,
        record.reasoning,
        record.recommended_action,
        int(record.human_override),
        record.indexed_at.isoformat(),
    )
    try:
        conn = await get_connection()
        try:
            cursor = await conn.execute(sql, values)
            await conn.commit()
            return cursor.lastrowid or 0
        finally:
            await conn.close()
    except Exception as exc:
        raise StorageError(f"Failed to insert event {record.post_id}") from exc


async def fetch_events(
    label: str | None = None,
    min_severity: float = 0.0,
    platform: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[CrisisEventRecord]:
    conditions = ["severity >= ?"]
    params: list[object] = [min_severity]
    if label:
        conditions.append("labels LIKE ?")
        params.append(f'%"{label}"%')
    if platform:
        conditions.append("platform = ?")
        params.append(platform)
    where = " AND ".join(conditions)
    sql = f"SELECT * FROM crisis_events WHERE {where} ORDER BY indexed_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    try:
        conn = await get_connection()
        try:
            cursor = await conn.execute(sql, params)
            rows = await cursor.fetchall()
            return [_row_to_record(row) for row in rows]
        finally:
            await conn.close()
    except Exception as exc:
        raise StorageError("Failed to fetch events") from exc


async def fetch_event_by_id(post_id: str) -> CrisisEventRecord | None:
    sql = "SELECT * FROM crisis_events WHERE post_id = ?"
    conn = await get_connection()
    try:
        cursor = await conn.execute(sql, (post_id,))
        row = await cursor.fetchone()
    finally:
        await conn.close()
    if row is None:
        return None
    return _row_to_record(row)


def _row_to_record(row: object) -> CrisisEventRecord:
    r = dict(row)  # type: ignore[call-overload]
    r["labels"] = json.loads(r["labels"])
    r["human_override"] = bool(r["human_override"])
    r["created_at"] = datetime.fromisoformat(r["created_at"])
    r["indexed_at"] = datetime.fromisoformat(r["indexed_at"])
    return CrisisEventRecord(**r)
