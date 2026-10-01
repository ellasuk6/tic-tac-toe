import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderApp } from "../test/render";

describe("NotFoundPage", () => {
  it("shows for an unknown URL and links back to the start page", async () => {
    const { user, router } = renderApp("/no-such-page");

    expect(screen.getByRole("heading", { name: "Page not found" })).toBeInTheDocument();
    await user.click(screen.getByRole("link", { name: "Go to the start page" }));

    expect(router.state.location.pathname).toBe("/");
    expect(screen.getByRole("button", { name: "New Game" })).toBeInTheDocument();
  });
});
