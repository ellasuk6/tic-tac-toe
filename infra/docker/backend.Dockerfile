# syntax=docker/dockerfile:1
#
# Backend image. Build context is ./backend (set in docker-compose.yml).
#
# Stage 1 ("builder") installs the locked dependencies with uv.
# Stage 2 ("runtime") copies only the result, with no uv and no build tools,
# and runs as an unprivileged user.

# uv's official image; we only copy its binary out of it.
FROM ghcr.io/astral-sh/uv:0.12.21 AS uv

# ---------- builder ----------
FROM python:3.14-slim-trixie AS builder
COPY --from=uv /uv /usr/local/bin/uv

# Compile .pyc files at build time, copy (not link) packages into the venv,
# and use the image's own Python instead of downloading one.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies first: this layer is cached until pyproject.toml or uv.lock changes.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev

# Then the application code and the database migrations.
COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic

# ---------- runtime ----------
FROM python:3.14-slim-trixie AS runtime

# A system user with no login shell and no password.
RUN groupadd --system app && useradd --system --gid app --home-dir /app --no-create-home app

WORKDIR /app
COPY --from=builder --chown=app:app /app /app

# /app/data holds the SQLite file; docker-compose mounts a named volume here.
RUN mkdir -p /app/data && chown app:app /app/data

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER app
EXPOSE 8000
# Bring the database up to date, then start the server. `exec` makes uvicorn the
# main process, so Control + C / `docker compose down` stops it cleanly.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
