"""Application entry point. uvicorn runs `app.main:app`."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.database import engine


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Startup: nothing to do. Tables are created by `alembic upgrade head`,
    # which runs before uvicorn starts (see infra/docker/backend.Dockerfile).
    yield
    # Shutdown: close every pooled database connection cleanly.
    engine.dispose()


app = FastAPI(title="Ultimate Tic-Tac-Toe API", version="0.1.0", lifespan=lifespan)
app.include_router(api_router)
