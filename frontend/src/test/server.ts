// MSW handlers for every API endpoint, plus a tiny in-memory "fake backend".
//
// The fake backend is test scaffolding, not game logic: it records a move and
// points the next player at the board matching the cell, just enough for UI
// tests to click through a few moves. The real rules live (and are tested) in the
// backend. Individual tests replace a handler with `server.use(...)` to simulate
// errors such as 404, 409, or 500.
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

import type { Game } from "../api/client";
import { makeGame, withMarks } from "./fixtures";

const games = new Map<number, Game>();
let nextId = 1;

export function resetFakeBackend(): void {
  games.clear();
  nextId = 1;
}

/** Put a game in the fake backend (for tests that start from a specific position). */
export function seedGame(game: Game): void {
  games.set(game.id, game);
  nextId = Math.max(nextId, game.id + 1);
}

const notFound = (id: number) =>
  HttpResponse.json(
    { code: "game_not_found", detail: `Game ${id} does not exist.` },
    { status: 404 },
  );

export const handlers = [
  http.post("*/api/v1/games", () => {
    const game = makeGame({ id: nextId++ });
    games.set(game.id, game);
    return HttpResponse.json(game, {
      status: 201,
      headers: { Location: `/api/v1/games/${game.id}` },
    });
  }),

  http.get("*/api/v1/games/:gameId", ({ params }) => {
    const id = Number(params.gameId);
    const game = games.get(id);
    return game ? HttpResponse.json(game) : notFound(id);
  }),

  http.post("*/api/v1/games/:gameId/moves", async ({ params, request }) => {
    const id = Number(params.gameId);
    const game = games.get(id);
    if (!game) return notFound(id);
    const { board, cell } = (await request.json()) as { board: number; cell: number };
    const player = game.current_player ?? "x";
    const updated: Game = {
      ...withMarks(game, [[board, cell, player]]),
      current_player: player === "x" ? "o" : "x",
      forced_board: cell,
      playable_boards: [cell],
      move_count: game.move_count + 1,
    };
    games.set(id, updated);
    return HttpResponse.json(updated, { status: 201 });
  }),
];

export const server = setupServer(...handlers);
