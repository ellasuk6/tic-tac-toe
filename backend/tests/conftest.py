"""Shared test fixtures.

API tests use httpx.AsyncClient with ASGITransport, which calls the FastAPI app
directly in memory: no server, no network. The async tests run on the `anyio`
pytest plugin, which ships with FastAPI, so no extra test dependency is needed.

Database tests get a brand-new SQLite file per test (in pytest's temporary folder),
so tests never share data and never touch backend/data/.
"""

import os

# Must happen before anything imports app.core: the app's default engine would
# otherwise point at the real ./data/uttt.db. Tests use their own databases below.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from collections.abc import AsyncIterator, Iterator  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import Engine  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

import app.models.game  # noqa: E402, F401  (registers the tables on Base.metadata)
from app.core.database import Base, create_db_engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def anyio_backend() -> str:
    # Run async tests on asyncio only (anyio would otherwise also try trio).
    return "asyncio"


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def db_engine(tmp_path: Path) -> Iterator[Engine]:
    engine = create_db_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(db_engine: Engine) -> Iterator[Session]:
    with Session(db_engine, autoflush=False, expire_on_commit=False) as s:
        yield s
