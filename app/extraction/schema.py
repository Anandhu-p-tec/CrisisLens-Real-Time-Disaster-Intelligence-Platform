from __future__ import annotations

from pydantic import BaseModel


class ExtractionResultSchema(BaseModel):
    post_id: str
    locations: list[str]
    coordinates: tuple[float, float] | None
    needs: list[str]
    entities: dict[str, list[str]]
