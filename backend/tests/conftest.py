"""Shared test fixtures.

API tests use httpx.AsyncClient with ASGITransport, which calls the FastAPI app
directly in memory: no server, no network. The async tests run on the `anyio`
pytest plugin, which ships with FastAPI, so no extra test dependency is needed.
"""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend() -> str:
    # Run async tests on asyncio only (anyio would otherwise also try trio).
    return "asyncio"


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
