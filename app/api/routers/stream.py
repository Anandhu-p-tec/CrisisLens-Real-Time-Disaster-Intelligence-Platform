from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime

from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from app.ingestion.stream_simulator import StreamSimulator
from app.pipeline.processor import CrisisProcessor

_logger = logging.getLogger(__name__)
router = APIRouter(tags=["stream"])


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)
        _logger.info("WebSocket client connected. Total: %d", len(self._connections))

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.remove(websocket)
        _logger.info("WebSocket client disconnected. Total: %d", len(self._connections))

    async def broadcast(self, payload: dict) -> None:
        dead: list[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_text(json.dumps(payload, default=str))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections.remove(ws)


manager = ConnectionManager()
_processor: CrisisProcessor | None = None
_simulator: StreamSimulator | None = None
_ingestion_task: asyncio.Task | None = None  # type: ignore[type-arg]


async def _ingestion_loop() -> None:
    global _processor, _simulator
    _processor = CrisisProcessor()
    _simulator = StreamSimulator()
    _logger.info("Ingestion loop started")
    async for post in _simulator.stream():
        try:
            record = await _processor.process(post)
            payload = {
                "post_id": record.post_id,
                "text": record.text,
                "labels": record.labels,
                "severity": record.severity,
                "confidence": record.confidence,
                "lat": record.lat,
                "lng": record.lng,
                "location_raw": record.location_raw,
                "reasoning": record.reasoning,
                "recommended_action": record.recommended_action,
                "human_override": record.human_override,
                "indexed_at": record.indexed_at.isoformat(),
            }
            await manager.broadcast(payload)
        except Exception as exc:
            _logger.error("Processing error: %s", exc)


@router.websocket("/ws/feed")
async def websocket_feed(websocket: WebSocket) -> None:
    global _ingestion_task
    await manager.connect(websocket)
    if _ingestion_task is None or _ingestion_task.done():
        _ingestion_task = asyncio.create_task(_ingestion_loop())
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
