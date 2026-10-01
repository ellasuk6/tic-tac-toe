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
**Alternative:** The rule in the original notes and in `script.js`: the opponent is forced into the same **board**, and forced moves alternate with free moves.
**Why not:** The product owner described the cell-based rule directly, with worked examples. `script.js` remains the reference for every other rule (win lines, decided boards, drawn boards not counting toward a line, game draw).

## D3 — Open product questions resolved by the team, NOT confirmed by the product owner
**Date:** 2026-09-30
**Decision:** With a Friday 1:00 p.m. deadline, the team chose the simplest reasonable answer for each open question. These are team assumptions, not product-owner answers. If the product owner answers differently, these are the first things to change.

| # | Question | Team assumption |
|---|---|---|
| A1 | Persistence | Games are saved in SQLite and survive a restart. The game id is in the page URL, so refreshing the page keeps the game. |
| A2 | List of past games | None. |
| A3 | New game mid-game | Starts immediately, no confirmation. The old game stays in the database untouched. |
| A4 | Move history | Not shown. |
| A5 | Undo | None. |
| A6 | Early termination | A small board is decided only when won or full. The game is a draw only when all 9 boards are decided with no line. |
| A7 | Illegal moves | The UI disables cells that cannot be played. The server still refuses them with a `409`, and the UI shows that message if one ever arrives. |
| A8 | Turn information | The UI shows whose turn it is and which board to play in (or "any open board"), and highlights playable boards. |
| A9 | After game over | The board freezes and a win or draw message is shown with the New Game button. |
| A10 | Winning-line highlight | None. |
| A11 | Player labels | "X" and "O" only. |
| A12 | Phone layout | No special mobile work beyond no horizontal scrolling. |
| A13 | Keyboard play | Every cell is a native button reachable with Tab. No arrow-key grid navigation. |
| A14 | First move | X moves first, and the first move is free (any board). |
| A15 | "Any spot" after being sent to a decided board | Any open cell in any undecided board. |
| A16 | Board and cell names | The UI uses the professor's names: boards A–I, cells 1–9. The API uses indices 0–8. |

**Alternative:** Wait for the product owner to answer each question.
**Why not:** There is not enough time before the deadline.

## D4 — Store only moves; compute all game state
**Date:** 2026-09-30
**Decision:** The database stores games and moves. Board contents, small-board results, whose turn, the forced board, playable boards, and game status are all computed by replaying the moves (at most 81).
**Alternative:** Store the board as JSON, or store status columns on the game.
**Why not:** The constitution says derived values are computed, never stored. Replaying 81 moves costs nothing at this scale.

## D5 — CI deferred
**Date:** 2026-09-30
**Decision:** GitHub Actions is not built unless the team approves it after the app is complete.
**Alternative:** Build CI early, as the constitution describes.
**Why not:** The product owner has not confirmed CI is required, and the deadline is short.

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
