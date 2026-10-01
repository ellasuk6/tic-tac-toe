// Typed API client. Every request and response type comes from schema.d.ts,
// which is GENERATED from the backend (`pnpm gen:api`). Never edit that file by hand.
import createClient from "openapi-fetch";

import type { components, paths } from "./schema";

export type Game = components["schemas"]["GameOut"];
export type SmallBoard = components["schemas"]["SmallBoardOut"];
export type Player = components["schemas"]["Player"];
type ErrorBody = components["schemas"]["ErrorOut"];

/** An error answer from the API, carrying the backend's `{code, detail}` envelope. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

// Same origin as the page: nginx (Docker) or the Vite proxy (pnpm dev) forwards /api.
const client = createClient<paths>({
  baseUrl: window.location.origin,
  // Look up fetch on every call instead of once at startup, so test tools (MSW)
  // that replace fetch after this module loads are still used.
  fetch: (request) => globalThis.fetch(request),
});

function isErrorBody(value: unknown): value is ErrorBody {
  return (
    typeof value === "object" &&
    value !== null &&
    typeof (value as ErrorBody).code === "string" &&
    typeof (value as ErrorBody).detail === "string"
  );
}

function toApiError(response: Response, body: unknown): ApiError {
  if (isErrorBody(body)) {
    return new ApiError(response.status, body.code, body.detail);
  }
  // Not our envelope, e.g. nginx answering 502 because the backend is down.
  return new ApiError(
    response.status,
    "unexpected_error",
    `The server answered with an unexpected error (${response.status}).`,
  );
}

export async function createGame(): Promise<Game> {
  const { data, error, response } = await client.POST("/api/v1/games");
  if (data === undefined) throw toApiError(response, error);
  return data;
}

export async function getGame(gameId: number): Promise<Game> {
  const { data, error, response } = await client.GET("/api/v1/games/{game_id}", {
    params: { path: { game_id: gameId } },
  });
  if (data === undefined) throw toApiError(response, error);
  return data;
}

export async function playMove(gameId: number, board: number, cell: number): Promise<Game> {
  const { data, error, response } = await client.POST("/api/v1/games/{game_id}/moves", {
    params: { path: { game_id: gameId } },
    body: { board, cell },
  });
  if (data === undefined) throw toApiError(response, error);
  return data;
}
