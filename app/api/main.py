from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    from app.repository.database import initialise_database

    await initialise_database()
    yield


app = FastAPI(
    title="CrisisLens",
    description="Real-Time Disaster Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routers import events
from app.api.routers import health
from app.api.routers import stream

app.include_router(health.router)
app.include_router(events.router)
app.include_router(stream.router)
