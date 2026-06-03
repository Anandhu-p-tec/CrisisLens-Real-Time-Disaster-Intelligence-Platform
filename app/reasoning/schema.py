from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ReasoningResultSchema(BaseModel):
    post_id: str
    reasoning: str
    recommended_action: str
    confidence_level: Literal["high", "medium", "low"]
    human_override: bool
    similar_event_ids: list[str]
