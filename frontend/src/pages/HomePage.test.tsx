import { screen } from "@testing-library/react";
import { delay, http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { renderApp } from "../test/render";
import { server } from "../test/server";

describe("HomePage", () => {
  it("shows the title and a New Game button", () => {
    renderApp("/");

    expect(screen.getByRole("heading", { name: "Ultimate Tic-Tac-Toe" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "New Game" })).toBeEnabled();
  });

  it("starts a game and opens its page", async () => {
    const { user, router } = renderApp("/");

    await user.click(screen.getByRole("button", { name: "New Game" }));

    expect(await screen.findByText("Player X: play in any open board.")).toBeInTheDocument();
    expect(router.state.location.pathname).toBe("/games/1");
  });

  it("disables the button while the game is being created", async () => {
    server.use(
      http.post("*/api/v1/games", async () => {
        await delay("infinite");
      }),
    );
    const { user } = renderApp("/");

    await user.click(screen.getByRole("button", { name: "New Game" }));

    expect(await screen.findByRole("button", { name: "Starting…" })).toBeDisabled();
  });

  it("shows an error when the game cannot be created, and trying again works", async () => {
    server.use(
      http.post(
        "*/api/v1/games",
        () => HttpResponse.json({ code: "oops", detail: "Database is busy." }, { status: 500 }),
        { once: true },
      ),
    );
    const { user, router } = renderApp("/");

    await user.click(screen.getByRole("button", { name: "New Game" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Could not start a game: Database is busy. Try again.",
    );
    await user.click(screen.getByRole("button", { name: "New Game" }));

    expect(await screen.findByText("Player X: play in any open board.")).toBeInTheDocument();
    expect(router.state.location.pathname).toBe("/games/1");
  });
});
