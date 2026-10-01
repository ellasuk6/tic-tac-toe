import { describe, expect, it } from "vitest";

import { makeGame } from "../test/fixtures";
import { boardLabel, cellLabel, statusMessage } from "./labels";

describe("labels", () => {
  it("uses the professor's names: boards A-I, cells 1-9", () => {
    expect([0, 4, 8].map(boardLabel)).toEqual(["A", "E", "I"]);
    expect([0, 4, 8].map(cellLabel)).toEqual(["1", "5", "9"]);
  });
});

describe("statusMessage", () => {
  it("names the board the current player is sent to", () => {
    const game = makeGame({ current_player: "o", forced_board: 6 });

    expect(statusMessage(game)).toBe("Player O: play in board G.");
  });

  it("says any open board on a free move", () => {
    expect(statusMessage(makeGame())).toBe("Player X: play in any open board.");
  });

  it.each([
    ["x_won", "Player X wins!"],
    ["o_won", "Player O wins!"],
  ] as const)("announces the winner for %s", (status, message) => {
    expect(statusMessage(makeGame({ status, current_player: null }))).toBe(message);
  });

  it("announces a draw", () => {
    const game = makeGame({ status: "draw", current_player: null });

    expect(statusMessage(game)).toMatch(/^It's a draw\./);
  });
});
