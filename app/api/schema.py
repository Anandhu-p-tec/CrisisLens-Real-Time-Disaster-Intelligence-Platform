from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import Generic
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseEnvelope(BaseModel, Generic[T]):
    data: T
    meta: dict[str, Any]

    @classmethod
    def ok(cls, data: T) -> "ResponseEnvelope[T]":
        return cls(
            data=data,
            meta={"timestamp": datetime.utcnow().isoformat(), "version": "1.0.0"},
        )


class EventResponse(BaseModel):
    post_id: str
    text: str
    platform: str
    created_at: datetime
    labels: list[str]
    severity: float
    confidence: float
    lat: float | None
    lng: float | None
    location_raw: str | None
    reasoning: str | None
    recommended_action: str | None
    human_override: bool
    indexed_at: datetime
