import { screen, within } from "@testing-library/react";
import { delay, http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { makeGame, withMarks } from "../test/fixtures";
import { renderApp } from "../test/render";
import { seedGame, server } from "../test/server";

const cell = (board: string, n: number, contents = "empty") =>
  screen.getByRole("button", { name: `Board ${board}, cell ${n}, ${contents}` });

const allCells = () => screen.getAllByRole("button", { name: /^Board [A-I], cell/ });

describe("GamePage states", () => {
  it("shows a loading message while the game is fetched", async () => {
    seedGame(makeGame({ id: 1 }));
    server.use(
      http.get("*/api/v1/games/:gameId", async () => {
        await delay("infinite");
      }),
    );

    renderApp("/games/1");

    expect(await screen.findByRole("status")).toHaveTextContent("Loading game…");
  });

  it("shows the empty state for a game with no moves", async () => {
    seedGame(makeGame({ id: 1 }));

    renderApp("/games/1");

    expect(await screen.findByText(/New game\. X goes first/)).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("Player X: play in any open board.");
    expect(allCells()).toHaveLength(81);
    expect(allCells().every((button) => !button.hasAttribute("disabled"))).toBe(true);
  });

  it("shows a populated game from the URL, e.g. after a page refresh", async () => {
    const game = withMarks(makeGame({ id: 5, move_count: 1 }), [[2, 4, "x"]]);
    seedGame({ ...game, current_player: "o", forced_board: 4, playable_boards: [4] });

    renderApp("/games/5");

    expect(await screen.findByText("Player O: play in board E.")).toHaveAttribute("role", "status");
    expect(cell("C", 5, "X")).toBeDisabled();
    expect(screen.queryByText(/New game\. X goes first/)).not.toBeInTheDocument();
  });

  it("shows an error with a Retry button that works", async () => {
    seedGame(makeGame({ id: 1 }));
    server.use(
      http.get(
        "*/api/v1/games/:gameId",
        () => HttpResponse.json({ code: "oops", detail: "Database is busy." }, { status: 500 }),
        { once: true },
      ),
    );
    const { user } = renderApp("/games/1");

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Could not load the game: Database is busy.",
    );
    await user.click(screen.getByRole("button", { name: "Retry" }));

    expect(await screen.findByText("Player X: play in any open board.")).toBeInTheDocument();
  });

  it("explains a server error that is not in the API's error format", async () => {
    server.use(
      http.get("*/api/v1/games/:gameId", () => new HttpResponse("Bad Gateway", { status: 502 })),
    );

    renderApp("/games/1");

    expect(await screen.findByRole("alert")).toHaveTextContent("unexpected error (502)");
  });

  it("says the game was not found when the server answers 404", async () => {
    renderApp("/games/99");

    expect(await screen.findByRole("alert")).toHaveTextContent("Game not found.");
    expect(screen.getByRole("button", { name: "New Game" })).toBeInTheDocument();
  });

  it("says the game was not found for a URL that is not a game id", async () => {
    renderApp("/games/abc");

    expect(await screen.findByRole("alert")).toHaveTextContent("Game not found.");
  });
});

describe("Playing", () => {
  it("places the mark and tells the next player where to play", async () => {
    seedGame(makeGame({ id: 1 }));
    const { user } = renderApp("/games/1");

    await user.click(await screen.findByRole("button", { name: "Board C, cell 5, empty" }));

    expect(await screen.findByRole("button", { name: "Board C, cell 5, X" })).toBeDisabled();
    expect(screen.getByRole("status")).toHaveTextContent("Player O: play in board E.");
  });

  it("only enables empty cells in the boards the server says are playable", async () => {
    const game = withMarks(makeGame({ id: 1, move_count: 1 }), [[2, 4, "x"]]);
    seedGame({ ...game, current_player: "o", forced_board: 4, playable_boards: [4] });

    renderApp("/games/1");

    expect(await screen.findByRole("button", { name: "Board E, cell 1, empty" })).toBeEnabled();
    expect(cell("A", 1)).toBeDisabled();
    expect(cell("I", 9)).toBeDisabled();
    expect(allCells().filter((button) => !button.hasAttribute("disabled"))).toHaveLength(9);
  });

  it("can be played with the keyboard alone", async () => {
    seedGame(makeGame({ id: 1 }));
    const { user } = renderApp("/games/1");
    await screen.findByRole("button", { name: "Board A, cell 1, empty" });

    await user.tab(); // the title link
    await user.tab(); // the first cell
    expect(cell("A", 1)).toHaveFocus();
    await user.keyboard("{Enter}");

    expect(await screen.findByRole("button", { name: "Board A, cell 1, X" })).toBeInTheDocument();
  });

  it("shows the server's message when a move is refused (409)", async () => {
    seedGame(makeGame({ id: 1 }));
    server.use(
      http.post("*/api/v1/games/:gameId/moves", () =>
        HttpResponse.json(
          { code: "cell_occupied", detail: "Cell 5 of board C is already taken." },
          { status: 409 },
        ),
      ),
    );
    const { user } = renderApp("/games/1");

    await user.click(await screen.findByRole("button", { name: "Board C, cell 5, empty" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Cell 5 of board C is already taken.",
    );
    expect(cell("C", 5)).toBeEnabled(); // nothing was placed
  });

  it("marks decided boards in words, not only by color", async () => {
    const game = makeGame({ id: 1, move_count: 5, current_player: "o" });
    game.boards[0] = { ...game.boards[0], status: "x_won" };
    game.boards[1] = { ...game.boards[1], status: "draw" };
    seedGame({ ...game, playable_boards: [2, 3, 4, 5, 6, 7, 8] });

    renderApp("/games/1");

    const boardA = await screen.findByRole("region", { name: "Board A, won by x" });
    expect(within(boardA).getByText("Won by X")).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Board B, draw" })).toHaveTextContent("Draw");
    expect(cell("A", 1)).toBeDisabled();
  });

  it("announces the winner and disables every cell when the game is won", async () => {
    seedGame(
      makeGame({
        id: 1,
        status: "x_won",
        current_player: null,
        playable_boards: [],
        move_count: 17,
      }),
    );

    renderApp("/games/1");

    expect(await screen.findByText("Player X wins!")).toHaveAttribute("role", "status");
    expect(allCells().every((button) => button.hasAttribute("disabled"))).toBe(true);
  });

  it("announces a draw", async () => {
    seedGame(makeGame({ id: 1, status: "draw", current_player: null, playable_boards: [] }));

    renderApp("/games/1");

    expect(await screen.findByText(/^It's a draw\./)).toHaveAttribute("role", "status");
  });

  it("starts a new game from the game page", async () => {
    seedGame(withMarks(makeGame({ id: 1, move_count: 1 }), [[0, 0, "x"]]));
    const { user, router } = renderApp("/games/1");
    await screen.findByRole("button", { name: "Board A, cell 1, X" });

    await user.click(screen.getByRole("button", { name: "New Game" }));

    expect(await screen.findByText(/New game\. X goes first/)).toBeInTheDocument();
    expect(router.state.location.pathname).toBe("/games/2");
    expect(cell("A", 1)).toBeEnabled();
  });
});
