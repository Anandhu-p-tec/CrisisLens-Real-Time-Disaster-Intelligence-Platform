from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel
from pydantic import Field


class CrisisLabel(StrEnum):
    FLOOD = "flood"
    FIRE = "fire"
    EARTHQUAKE = "earthquake"
    MEDICAL = "medical"


class ClassificationResultSchema(BaseModel):
    post_id: str
    labels: list[CrisisLabel]
    severity: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    raw_logits: list[float]
