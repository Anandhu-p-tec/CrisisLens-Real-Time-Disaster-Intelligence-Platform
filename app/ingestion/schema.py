from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class RawPostSchema(BaseModel):
    post_id: str
    text: str
    platform: Literal["twitter", "reddit", "simulator"]
    created_at: datetime
