# Decisions

Every choice that had a real alternative. Newest at the bottom.

---

## D1 — Continue in the existing repo; tag the prototype
**Date:** 2026-09-30
**Decision:** Tag the last prototype commit as `prototype-vanilla-js`, remove the prototype files from `main`, and rebuild `main` in the constitution's layout.
**Alternative:** Start a new repository, or keep the prototype in a `prototype/` folder on `main`.
**Why not:** The tag preserves the prototype permanently. A `prototype/` folder is not in the constitution's fixed layout.

## D2 — Move placement rule: the professor's statement overrides the earlier notes and the prototype
**Date:** 2026-09-30
**Decision:** The **cell** index of a move (0–8) sets the board the opponent must play in next, on every move. If that board is already decided (won or full), the opponent may play any open cell in any undecided board.
**Alternative:** the opponent is forced into the same **board**, and forced moves alternate with free moves.
**Why not:** `script.js` remains the reference for every other rule (win lines, decided boards, drawn boards not counting toward a line, game draw).

## D4 — Store only moves; compute all game state
**Date:** 2026-09-30
**Decision:** The database stores games and moves. Board contents, small-board results, whose turn, the forced board, playable boards, and game status are all computed by replaying the moves (at most 81).
**Alternative:** Store the board as JSON, or store status columns on the game.
**Why not:** The constitution says derived values are computed, never stored. Replaying 81 moves costs nothing at this scale.

## D5 — CI deferred
**Date:** 2026-09-30
**Decision:** GitHub Actions is not built unless the team approves it after the app is complete.
**Alternative:** Build CI early, as the constitution describes.
**Why not:** The product owner has not confirmed CI is required.

## D6 — Async API tests run on anyio's pytest plugin
**Date:** 2026-09-30
**Decision:** API tests use `httpx.AsyncClient` with `ASGITransport` (as the constitution requires) and are marked `@pytest.mark.anyio`.
**Alternative:** Add `pytest-asyncio`.
**Why not:** It is not on the locked stack list, and `anyio` is already installed as part of FastAPI.

## D7 — Settings module and lifespan hook deferred to the database stage
**Date:** 2026-09-30
**Decision:** Stage 1 has no settings module and no `lifespan` handler. Both arrive in Stage 4, when `DATABASE_URL` and the database engine exist.
**Alternative:** Add empty versions now.
**Why not:** There is nothing to configure or start up yet, and empty code cannot be meaningfully tested.

## D8 — Python version range
**Date:** 2026-09-30
**Decision:** `requires-python = ">=3.13"` in `pyproject.toml`; `.python-version` pins 3.14 for local work and Docker.
**Alternative:** `>=3.14` (what `uv init` generated).
**Why not:** The constitution names 3.13 as the minimum.

## D9 — Ruff rule set
**Date:** 2026-09-30
**Decision:** Ruff checks `E, F, I, UP, B, SIM` with a 100-character line length.
**Alternative:** Ruff's defaults (`E, F` only, 88 characters).
**Why not:** The extra rules catch import order, outdated syntax, and likely bugs at no cost.

## D10 — TypeScript pinned to 5.9.x
**Date:** 2026-09-30
**Decision:** `"typescript": "~5.9.3"` (patch updates only).
**Alternative:** The newest TypeScript, which is now 7.0.
**Why not:** The constitution locks TypeScript 5.x.

## D11 — nginx proxies `/api/` to the backend; the backend port is not published
**Date:** 2026-09-30
**Decision:** The browser only talks to nginx on port 8080. nginx serves the React files and forwards `/api/` to `backend:8000` on the Docker network.
**Alternative:** Publish the backend on its own port and enable CORS in FastAPI.
**Why not:** One origin means no CORS setup, and the backend is not exposed to anything but nginx.

## D12 — Non-root nginx via `nginxinc/nginx-unprivileged`
**Date:** 2026-09-30
**Decision:** The frontend runtime image is NGINX's own unprivileged image (runs as user `nginx`, listens on 8080).
**Alternative:** The standard `nginx` image modified by hand to drop root.
**Why not:** The constitution requires non-root users; the unprivileged image does this correctly out of the box.

## D13 — nginx.conf is baked into the image through a second build context
**Date:** 2026-09-30
**Decision:** Compose passes `./infra/docker` to the frontend build as an extra context named `infra`, and the Dockerfile copies `nginx.conf` from it.
**Alternative:** Mount `nginx.conf` into the container as a volume at run time.
**Why not:** A mounted file makes the image depend on the host's files; the constitution's layout keeps nginx.conf in `infra/docker/` but the image should be self-contained.

## D14 — `.env.example` files deferred to the database stage
**Date:** 2026-09-30
**Decision:** No `.env.example` yet. It arrives in Stage 4 with `DATABASE_URL`, the first setting either app reads.
**Alternative:** Add empty example files now.
**Why not:** An example file listing no variables documents nothing.

## D15 — Rules engine is pure functions over an immutable game state
**Date:** 2026-10-01
**Decision:** `app/services/rules.py` has no database or HTTP code. `apply_move(state, move)` returns a new frozen `GameState`; `replay(moves)` rebuilds any game from its move list (see D4).
**Alternative:** A `Game` class that changes its own board in place, or rules mixed into the service that saves to the database.
**Why not:** Pure functions can be tested exhaustively with no setup, and a refused move cannot leave a half-changed board behind.

## D16 — Domain enums live in `app/models/enums.py`
**Date:** 2026-10-01
**Decision:** `Player`, `BoardStatus`, and `GameStatus` are `StrEnum`s in a models file that imports nothing from SQLAlchemy.
**Alternative:** Put them in `app/core/` or inside `rules.py`.
**Why not:** The constitution puts `StrEnum`s in the model layer; keeping the file SQLAlchemy-free lets the pure rules engine import it too.

## D17 — Two separate error codes for "wrong board"
**Date:** 2026-10-01
**Decision:** `board_not_playable` when the player was sent to a different board; `board_decided` when the player had a free move but chose a won or full board.
**Alternative:** One code for both.
**Why not:** They are different mistakes and the message to the player differs ("you must play in board E" vs "board A is already decided").

## D18 — Out-of-range board or cell numbers are a programming error in the rules layer
**Date:** 2026-10-01
**Decision:** `Move` raises `ValueError` for numbers outside 0–8. The API schema (Stage 5) rejects them first with a `422`.
**Alternative:** A domain error with its own `409` code.
**Why not:** The constitution says schema failures are `422`, never a business-rule `409`.


## D20 — The player is not stored on a move
**Date:** 2026-10-01
**Decision:** The `moves` table stores `seq`, `board`, and `cell`. The player is derived: even `seq` is X, odd is O.
**Alternative:** A `player` column, as an integrity check.
**Why not:** The constitution says derived values are computed, never stored. The rules engine already alternates players by move order.

## D21 — Settings read with `os.environ`, not `pydantic-settings`
**Date:** 2026-10-01
**Decision:** `app/core/config.py` is a small frozen dataclass filled from environment variables.
**Alternative:** The `pydantic-settings` package.
**Why not:** It is not on the stack list, and the constitution says not to add dependencies without asking. With one setting, plain `os.environ` is enough. Revisit when settings grow.

## D22 — PostgreSQL is ready in configuration only
**Date:** 2026-10-01
**Decision:** `DATABASE_URL` accepts a `postgresql+psycopg://` URL and docker-compose has a commented-out `db` service, but the `psycopg` driver is not installed.
**Alternative:** Install `psycopg[binary]` now.
**Why not:** Nothing uses PostgreSQL yet; an unused driver is an unused dependency. Switching needs one command: `uv add "psycopg[binary]"`.

## D23 — Migrations run when the backend container starts
**Date:** 2026-10-01
**Decision:** The container command is `alembic upgrade head && exec uvicorn ...`. The FastAPI `lifespan` hook only closes database connections on shutdown.
**Alternative:** Run migrations inside `lifespan`, or create tables with `Base.metadata.create_all`.
**Why not:** Keeping migrations outside the app means the app never changes its own schema while serving, and `create_all` cannot apply later changes to an existing database. This also closes D7.

## D24 — Timestamps go through a `UTCDateTime` column type
**Date:** 2026-10-01
**Decision:** All `*_at` columns use a small SQLAlchemy type that refuses timezone-less datetimes and always returns UTC-aware datetimes.
**Alternative:** Plain `DateTime(timezone=True)`.
**Why not:** SQLite drops the timezone, so timestamps would come back "naive" from SQLite but aware from PostgreSQL. The constitution requires UTC.

## D25 — Repositories flush; services commit
**Date:** 2026-10-01
**Decision:** Repository functions call `session.flush()` (so new rows get ids) but never `commit()`. The service layer (Stage 5) commits once per request.
**Alternative:** Each repository function commits.
**Why not:** A move must be validated and saved as one unit; committing inside the repository would make that impossible.

## D26 — No pagination tests for now
**Date:** 2026-10-01
**Decision:** The constitution's repository tests for filtering, sorting, and pagination are not written.
**Alternative:** Build a paginated games list anyway.
**Why not:** There is no list endpoint (A2: no list of past games), so there is nothing to paginate. These tests arrive with the first list endpoint.

## D27 — First migration edited by hand; a test checks migrations match models
**Date:** 2026-10-01
**Decision:** Alembic's autogenerated migration referenced app code (`app.core.database.UTCDateTime`) without importing it. It was rewritten to use plain `sa.DateTime(timezone=True)`. `tests/test_migrations.py` fails if the migrated database ever differs from the models.
**Alternative:** Keep the generated file and add the import.
**Why not:** Migrations must keep working even after app code changes, so they should not import it.

## D28 — Every error uses the envelope, including 422, 404, and 405 from the framework
**Date:** 2026-10-01
**Decision:** `app/api/v1/errors.py` registers three handlers: domain errors (404 / 409), request validation (422, `validation_error`), and framework HTTP errors (e.g. unknown URL → 404 `not_found`). All return `{"code", "detail"}`.
**Alternative:** Only handle domain errors and keep FastAPI's default `{"detail": [...]}` for 422.
**Why not:** The constitution says every error returns the same envelope, and one shape is simpler for the frontend.

## D29 — Playing a move returns the whole game; `Location` points at the game
**Date:** 2026-10-01
**Decision:** `POST /api/v1/games/{id}/moves` returns `201` with the updated game state, and its `Location` header is `/api/v1/games/{id}`.
**Alternative:** Return only the move, with `Location: /api/v1/games/{id}/moves/{seq}`.
**Why not:** The frontend needs the new board after every move anyway, so this saves a request. A per-move URL would point at nothing, since there is no endpoint for reading a single move (A4: no move history).

## D30 — The server decides whose turn it is
**Date:** 2026-10-01
**Decision:** The move request body is only `{"board", "cell"}`. The player is whoever's turn the replayed game says it is.
**Alternative:** The client sends the player and the server checks it.
**Why not:** One shared computer means there is no way for a request to be "the wrong player", so a `not_your_turn` check would guard nothing.

## D31 — A simultaneous second move is refused with `409 move_conflict`
**Date:** 2026-10-01
**Decision:** If two requests try to save the same move number (e.g. a double click), the database's unique `(game_id, seq)` rule keeps the first, and the second gets `409 move_conflict`.
**Alternative:** Lock the game row while a move is processed.
**Why not:** SQLite has no row locks, and the unique rule already guarantees a game's moves can never be corrupted.

## D32 — Test move sequences live in one shared module
**Date:** 2026-10-01
**Decision:** `tests/game_sequences.py` holds the legal move sequences used by the rules, service, and API tests.
**Alternative:** Copy them into each test file.
**Why not:** A copied 25-move sequence could silently drift between files.

## D33 — Frontend tool versions: locked majors where the constitution names one
**Date:** 2026-10-01
**Decision:** Vitest 4.1, MSW 2.15, ESLint 9.39, and TypeScript 5.9, even though Vitest 5, MSW 3, ESLint 10, and TypeScript 7 exist. React Router 8 and TanStack Query 5 are the current majors, as the constitution asks.
**Alternative:** The newest version of everything.
**Why not:** The constitution locks those majors for every team.

## D34 — The OpenAPI snapshot and generated types are committed
**Date:** 2026-10-01
**Decision:** `frontend/openapi.json` (exported from the backend) and `frontend/src/api/schema.d.ts` (generated from it) are committed. `pnpm gen:api` regenerates both after any backend API change.
**Alternative:** Generate the types during every frontend build.
**Why not:** The frontend Docker build would then need the whole backend. Committing them also makes API changes visible in code review.

## D35 — The API client looks up `fetch` on every call
**Date:** 2026-10-01
**Decision:** `createClient({ fetch: (request) => globalThis.fetch(request) })`.
**Alternative:** openapi-fetch's default, which saves `fetch` once when the module loads.
**Why not:** MSW replaces `fetch` after modules load, so with the default every test request escaped to the real network ("fetch failed"). Browsers behave the same either way.

## D36 — pnpm is told not to run msw's install script
**Date:** 2026-10-01
**Decision:** `allowBuilds: { msw: false }` in `frontend/pnpm-workspace.yaml`.
**Alternative:** Allow the script.
**Why not:** pnpm 12 fails `pnpm install` (including the Docker build) on any unreviewed install script. msw's only copies a browser helper file; our tests run msw in Node and do not need it.

## D37 — Tests use a small fake backend built with MSW
**Date:** 2026-10-01
**Decision:** `src/test/server.ts` has handlers for every endpoint and an in-memory list of games, so UI tests can click through moves. It records moves and points the next player at the board matching the cell, but does not check rules. Individual tests swap in 404, 409, 500, and 502 answers.
**Alternative:** Fixed responses only.
**Why not:** User-flow tests need the board to change after a click. The real rules are tested in the backend; the frontend applies none.

## D38 — The UI applies no game rules
**Date:** 2026-10-01
**Decision:** A cell is clickable only if the server's `playable_boards` contains its board, the cell is empty, and no move is being sent. Status text comes from the server's `status`, `current_player`, and `forced_board`.
**Alternative:** Recompute legal moves in the browser.
**Why not:** The rules would then live in two places and could disagree.

## D39 — A start page with a New Game button
**Date:** 2026-10-01
**Decision:** `/` shows the title, a one-paragraph explanation, and New Game. New Game creates the game and opens `/games/{id}`.
**Alternative:** Create a game automatically whenever `/` is opened.
**Why not:** Every visit or refresh of `/` would leave an unused game in the database.

## D40 — No client-side validation tests
**Date:** 2026-10-01
**Decision:** The constitution's per-rule validation-message tests are not written.
**Alternative:** n/a
**Why not:** The app has no form inputs. Moves are buttons, and the server is the only judge of a move.

## D41 — `frontend/.env.example` documents the dev proxy
**Date:** 2026-10-01
**Decision:** `pnpm dev` forwards `/api` to `API_PROXY_TARGET` (default `http://127.0.0.1:8000`). This closes D14.
**Alternative:** Hard-code the backend address.
**Why not:** The constitution requires `.env.example` in both apps, and the address is the only frontend setting.

## D42 — Nothing is shown by color alone
**Date:** 2026-10-01
**Decision:** Decided boards show "Won by X", "Won by O", or "Draw" in text; the board to play in is named in the status line as well as highlighted; X and O are letters, not just colors; every cell has a spoken label like "Board E, cell 5, empty".
**Alternative:** Color-coded boards and marks only.
**Why not:** The constitution's accessibility floor.

## D43 — No CI for this assignment (closes D5)
**Date:** 2026-10-01
**Decision:** No `.github/workflows/ci.yml`. The team decided CI is not needed for the warmup.
**Alternative:** The constitution's GitHub Actions workflow (lint, typecheck, and test both sides on every push).
**Why not:** The product owner has not required it for this assignment. All the same checks are documented in the README and were run by hand before each commit.

## D44 — End-to-end tests run against the app already started with Docker Compose
**Date:** 2026-10-01
**Decision:** `pnpm test:e2e` expects `docker compose up` to be running and tests `http://localhost:8080` (override with `E2E_BASE_URL`). Two happy-path tests: the professor's example move plus a page refresh, and a complete game to an X win.
**Alternative:** Let Playwright start the backend and the Vite dev server by itself (`webServer`).
**Why not:** Testing the real Docker stack (nginx, the built frontend, migrations on start) is what the product owner grades. A full drawn game is not tested end to end; draws are covered by the backend and frontend tests.
