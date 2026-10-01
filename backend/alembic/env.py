"""Alembic migration environment.

Run migrations with:   uv run alembic upgrade head
Create a new one with: uv run alembic revision --autogenerate -m "describe the change"
"""

from logging.config import fileConfig

from alembic import context

import app.models.game  # noqa: F401  (registers the tables on Base.metadata)
from app.core.config import settings
from app.core.database import Base, create_db_engine

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Tests may pass their own URL (config.set_main_option); otherwise use DATABASE_URL.
database_url = config.get_main_option("sqlalchemy.url") or settings.database_url


def run_migrations_offline() -> None:
    """Write the SQL to the screen instead of running it (alembic upgrade head --sql)."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_db_engine(database_url)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite cannot ALTER most things in place; "batch" mode copies the table instead.
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
