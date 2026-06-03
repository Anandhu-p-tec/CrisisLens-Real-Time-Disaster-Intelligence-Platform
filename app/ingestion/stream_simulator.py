from __future__ import annotations

import asyncio
from datetime import datetime
from datetime import timezone
from typing import AsyncGenerator
from uuid import uuid4

import pandas as pd
from pathlib import Path

from app.core.config import settings
from app.ingestion.schema import RawPostSchema


class StreamSimulator:
    def __init__(
        self,
        speed_factor: float | None = None,
        batch_size: int = 1,
    ) -> None:
        self._speed_factor: float = (
            speed_factor if speed_factor is not None else settings.SIMULATOR_SPEED_FACTOR
        )
        self._batch_size: int = batch_size
        self._df: pd.DataFrame = pd.read_csv(Path("data/processed/crisis_dataset.csv"))
        self._index: int = 0

    async def next_post(self) -> RawPostSchema:
        row = self._df.iloc[self._index % len(self._df)]
        self._index += 1
        post = RawPostSchema(
            post_id=f"sim_{self._index}_{uuid4().hex[:8]}",
            text=str(row["text"]),
            platform="simulator",
            created_at=datetime.now(tz=timezone.utc),
        )
        await asyncio.sleep(1.0 / self._speed_factor)
        return post

    async def stream(self) -> AsyncGenerator[RawPostSchema, None]:
        while True:
            yield await self.next_post()
