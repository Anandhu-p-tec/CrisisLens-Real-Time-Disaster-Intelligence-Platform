from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CrisisEventRecord(BaseModel):
    id: int | None = None
    post_id: str
    text: str
    platform: str
    created_at: datetime
    labels: list[str]
    severity: float
    confidence: float
    lat: float | None = None
    lng: float | None = None
    location_raw: str | None = None
    reasoning: str | None = None
    recommended_action: str | None = None
    human_override: bool = False
    indexed_at: datetime
