from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import Session

from app.core.config import DEFAULT_DATABASE_URL, load_settings
from app.core.database import create_db_engine
from app.models.game import Game

# --- Settings -------------------------------------------------------------------------


def test_database_url_defaults_to_a_local_sqlite_file(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    assert load_settings().database_url == DEFAULT_DATABASE_URL == "sqlite:///./data/uttt.db"


def test_database_url_comes_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@db:5432/uttt")

    assert load_settings().database_url == "postgresql+psycopg://u:p@db:5432/uttt"


# --- Engine ---------------------------------------------------------------------------


def test_sqlite_engine_creates_the_missing_data_folder(tmp_path: Path) -> None:
    db_file = tmp_path / "nested" / "folder" / "app.db"

    engine = create_db_engine(f"sqlite:///{db_file}")
    with engine.connect():
        pass
    engine.dispose()

    assert db_file.exists()


def test_sqlite_engine_enforces_foreign_keys(tmp_path: Path) -> None:
    engine = create_db_engine(f"sqlite:///{tmp_path / 'fk.db'}")

    with engine.connect() as connection:
        enabled = connection.execute(text("PRAGMA foreign_keys")).scalar()
    engine.dispose()

    assert enabled == 1


# --- Timestamps -----------------------------------------------------------------------


def test_timestamps_in_other_timezones_are_stored_as_utc(session: Session) -> None:
    eastern = timezone(timedelta(hours=-4))
    game = Game(created_at=datetime(2026, 10, 1, 9, 0, tzinfo=eastern))
    session.add(game)
    session.commit()
    session.expunge_all()

    reloaded = session.get(Game, game.id)

    assert reloaded is not None
    assert reloaded.created_at == datetime(2026, 10, 1, 13, 0, tzinfo=UTC)
    assert reloaded.created_at.tzinfo is UTC


def test_timestamps_without_a_timezone_are_refused(session: Session) -> None:
    session.add(Game(created_at=datetime(2026, 10, 1, 9, 0)))

    with pytest.raises(StatementError, match="timezone-aware"):
        session.flush()
