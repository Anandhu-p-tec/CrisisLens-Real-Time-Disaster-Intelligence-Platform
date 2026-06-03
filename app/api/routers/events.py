from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query

from app.api.schema import EventResponse
from app.api.schema import ResponseEnvelope
from app.repository.events import fetch_event_by_id
from app.repository.events import fetch_events
from app.repository.schema import CrisisEventRecord

router = APIRouter(prefix="/events", tags=["events"])


def _to_response(record: CrisisEventRecord) -> EventResponse:
    return EventResponse(
        post_id=record.post_id,
        text=record.text,
        platform=record.platform,
        created_at=record.created_at,
        labels=record.labels,
        severity=record.severity,
        confidence=record.confidence,
        lat=record.lat,
        lng=record.lng,
        location_raw=record.location_raw,
        reasoning=record.reasoning,
        recommended_action=record.recommended_action,
        human_override=record.human_override,
        indexed_at=record.indexed_at,
    )


@router.get("", response_model=ResponseEnvelope[list[EventResponse]])
async def list_events(
    label: str | None = Query(default=None),
    min_severity: float = Query(default=0.0, ge=0.0, le=1.0),
    platform: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ResponseEnvelope[list[EventResponse]]:
    records = await fetch_events(
        label=label,
        min_severity=min_severity,
        platform=platform,
        limit=limit,
        offset=offset,
    )
    return ResponseEnvelope.ok([_to_response(r) for r in records])


@router.get("/{post_id}", response_model=ResponseEnvelope[EventResponse])
async def get_event(post_id: str) -> ResponseEnvelope[EventResponse]:
    record = await fetch_event_by_id(post_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return ResponseEnvelope.ok(_to_response(record))
