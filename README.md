# Ultimate Tic-Tac-Toe

Two players, X and O, share one computer and play Ultimate Tic-Tac-Toe in the browser:
a 3x3 grid of small tic-tac-toe boards (81 cells).

## Run it

**Requires:** Docker Desktop, running.

```
docker compose up --build
```

Wait until the log shows health checks repeating, then open **http://localhost:8080**.

Stop with **Control + C**, then:

```
docker compose down       # stop (saved games are kept)
docker compose down -v    # stop and delete all saved games
```

## The rules, as implemented

- X moves first and may play anywhere.
- **The cell you play picks the board your opponent must play in next.** 
- A small board is won with three in a row. A full board with no winner is a draw. A won or
  drawn board accepts no more moves.
- If you would be sent to a won or drawn board, you may instead play in any open board.
- Win three small boards in a row (row, column, or diagonal) to win the game. Drawn boards
  never count toward a line.
- If every board is decided and nobody has three in a row, the game is a draw.
- **New Game** starts over at any time. A game's address survives a refresh.

## How it is built

```
browser ──> nginx (frontend container, port 8080)
              ├── /         React app (built static files)
              └── /api/...  ──> FastAPI + uvicorn (backend container) ──> SQLite (volume)
```

| Part | Stack |
|---|---|
| Backend | Python 3.14, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, SQLite, uv |
| Frontend | React 19, TypeScript 5.9, Vite 8, Tailwind CSS 4, React Router 8, TanStack Query 5, pnpm |
| Tests | pytest + httpx; Vitest + Testing Library + MSW; Playwright |

Backend layers (`backend/app/`): the **rules** are pure functions in `services/rules.py`;
`services/game_service.py` loads a game's moves, replays them through the rules, validates
the new move, and saves it; `repositories/` reads and writes rows; `api/v1/` only translates
HTTP. Only moves are stored. Board state, winners, and whose turn it is are always computed
from the moves.

### API

| Request | Success | Errors |
|---|---|---|
| `POST /api/v1/games` | `201` new game | |
| `GET /api/v1/games/{id}` | `200` game state | `404`, `422` |
| `POST /api/v1/games/{id}/moves` `{"board": 0-8, "cell": 0-8}` | `201` updated game | `404`, `409`, `422` |

Every error is `{"code": "...", "detail": "..."}`. The `409` codes are `game_over`,
`board_not_playable`, `board_decided`, `cell_occupied`, and `move_conflict`.
Interactive docs: run the backend locally (below) and open http://127.0.0.1:8000/docs.

## Develop and test without Docker

**Requires:** uv, Node 24, pnpm (via `corepack enable`).

### Backend (from `backend/`)

```
uv sync
uv run alembic upgrade head            # create the local database (backend/data/)
uv run uvicorn app.main:app --reload   # http://127.0.0.1:8000/docs

uv run ruff check . && uv run ruff format --check . && uv run mypy
uv run pytest --cov=app --cov-report=term-missing:skip-covered --cov-report=html --cov-fail-under=80
```

### Frontend (from `frontend/`)

```
pnpm install
pnpm dev                               # http://localhost:5173 (needs the backend running)

pnpm typecheck && pnpm lint && pnpm format:check
pnpm test:cov
pnpm gen:api                           # after any backend API change: regenerate the API types
```

### End-to-end test (from `frontend/`, with `docker compose up` running)

```
pnpm e2e:install                       # once: downloads Playwright's Chromium
pnpm test:e2e
```

## History

The original plain-JavaScript prototype is preserved at the git tag `prototype-vanilla-js`.
Changes are listed in [`CHANGELOG.md`](CHANGELOG.md).
