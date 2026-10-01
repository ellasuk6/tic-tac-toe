"""Database engine, session factory, and the declarative base for all models.

Synchronous SQLAlchemy on purpose (the constitution excludes the async engine).
FastAPI runs synchronous endpoints in a thread pool, which is fine at this scale.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import DateTime, Engine, create_engine, event
from sqlalchemy.engine import Dialect, make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.types import TypeDecorator

from app.core.config import settings


class Base(DeclarativeBase):
    """Every model inherits from this. Alembic reads Base.metadata to know the tables."""


class UTCDateTime(TypeDecorator[datetime]):
    """Stores UTC timestamps and always returns timezone-aware UTC datetimes.

    SQLite has no timezone support, so it hands back "naive" datetimes. Without this,
    a timestamp read from SQLite and one read from PostgreSQL would look different.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("Timestamps must be timezone-aware (use datetime.now(UTC)).")
        return value.astimezone(UTC) if value is not None else None

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def utc_now() -> datetime:
    return datetime.now(UTC)


def create_db_engine(database_url: str) -> Engine:
    url = make_url(database_url)
    connect_args: dict[str, Any] = {}

    if url.get_backend_name() == "sqlite":
        # FastAPI may use a session on a different thread than the one that opened it.
        connect_args["check_same_thread"] = False
        # Create the folder for a file database (e.g. ./data/) if it is missing.
        if url.database and url.database != ":memory:":
            Path(url.database).parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(database_url, connect_args=connect_args)

    if url.get_backend_name() == "sqlite":
        # SQLite ignores foreign keys unless you turn them on for every connection.
        @event.listens_for(engine, "connect")
        def _enable_sqlite_foreign_keys(dbapi_connection: Any, _record: Any) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = create_db_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    """FastAPI dependency (used from Stage 5): one session per request, always closed."""
    with SessionLocal() as session:
        yield session
