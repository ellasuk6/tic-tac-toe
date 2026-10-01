"""The migrations must build exactly the tables the models describe.

If someone changes a model and forgets to write a migration, the comparison test
fails, before Docker ever runs `alembic upgrade head` against a real database.
"""

from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import inspect

import app.models.game  # noqa: F401  (registers the tables on Base.metadata)
from app.core.database import Base, create_db_engine

BACKEND_DIR = Path(__file__).resolve().parents[1]


def alembic_config(database_url: str) -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def test_upgrade_creates_the_tables(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'migrated.db'}"

    command.upgrade(alembic_config(url), "head")

    engine = create_db_engine(url)
    tables = set(inspect(engine).get_table_names())
    engine.dispose()
    assert {"games", "moves", "alembic_version"} <= tables


def test_migrations_match_the_models(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'migrated.db'}"
    command.upgrade(alembic_config(url), "head")

    engine = create_db_engine(url)
    with engine.connect() as connection:
        differences = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    engine.dispose()

    assert differences == []


def test_downgrade_removes_the_tables(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'migrated.db'}"
    config = alembic_config(url)
    command.upgrade(config, "head")

    command.downgrade(config, "base")

    engine = create_db_engine(url)
    tables = set(inspect(engine).get_table_names())
    engine.dispose()
    assert tables.isdisjoint({"games", "moves"})
