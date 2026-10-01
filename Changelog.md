# Changelog

## [Unreleased]

### Added
- Project restructured into the course constitution layout.
- `DECISIONS.md`, `README.md`, `CHANGELOG.md`, `.gitignore`.
- Backend skeleton: uv project (FastAPI, uvicorn), `GET /api/v1/health`, Ruff, mypy strict, pytest with coverage.
- Minimal frontend (Vite 8, React 19, TypeScript 5.9) placeholder page.
- Docker Compose: backend (uvicorn, non-root) and frontend (nginx, non-root) with healthchecks, a named volume for SQLite, and a commented-out PostgreSQL service.
- Game rules engine (`app/services/rules.py`): professor's cell-picks-the-board rule, small-board and game wins and draws, free move when sent to a decided board, with 76 tests.
- Database: SQLAlchemy models for games and moves, first Alembic migration (run automatically when the backend container starts), repository functions, `DATABASE_URL` setting and `backend/.env.example`.
- API: `POST /api/v1/games`, `GET /api/v1/games/{id}`, `POST /api/v1/games/{id}/moves`, with the `{code, detail}` error envelope on every error (404, 409, 422).

### Removed
- Plain-JavaScript prototype files from `main` (preserved at tag `prototype-vanilla-js`).
