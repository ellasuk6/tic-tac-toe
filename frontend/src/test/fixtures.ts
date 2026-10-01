// Test data shaped exactly like the API's GameOut (the type is generated from it).
import type { Game, Player } from "../api/client";

type Mark = Player | null;

export function makeGame(overrides: Partial<Game> = {}): Game {
  return {
    id: 1,
    created_at: "2026-10-01T13:00:00Z",
    status: "in_progress",
    current_player: "x",
    forced_board: null,
    playable_boards: [0, 1, 2, 3, 4, 5, 6, 7, 8],
    move_count: 0,
    boards: Array.from({ length: 9 }, (_, index) => ({
      index,
      status: "open" as const,
      cells: Array<Mark>(9).fill(null),
    })),
    ...overrides,
  };
}

/** Copy of `game` with `marks` placed: a list of [board, cell, player]. */
export function withMarks(game: Game, marks: [number, number, Player][]): Game {
  const boards = game.boards.map((b) => ({ ...b, cells: [...b.cells] }));
  for (const [board, cell, player] of marks) boards[board].cells[cell] = player;
  return { ...game, boards };
}
