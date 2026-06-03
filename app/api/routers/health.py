from __future__ import annotations

from fastapi import APIRouter

from app.api.schema import ResponseEnvelope

router = APIRouter(tags=["health"])


@router.get("/health", response_model=ResponseEnvelope[dict])
async def health_check() -> ResponseEnvelope[dict]:
    return ResponseEnvelope.ok({"status": "ok"})
