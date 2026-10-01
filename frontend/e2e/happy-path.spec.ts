// Happy-path smoke tests (constitution: Playwright, happy path only).
// These run against the full stack: browser -> nginx -> FastAPI -> SQLite.
import { expect, type Page, test } from "@playwright/test";

const BOARDS = "ABCDEFGHI";

/** Click a cell by the API's 0-8 numbers; the page labels them A-I and 1-9. */
async function play(page: Page, board: number, cell: number) {
  const emptyCell = page.getByRole("button", {
    name: `Board ${BOARDS[board]}, cell ${cell + 1}, empty`,
    exact: true,
  });
  await emptyCell.click();
  // Wait for the server's answer: the cell is no longer empty.
  await expect(emptyCell).toHaveCount(0);
}

async function startNewGame(page: Page) {
  await page.goto("/");
  await page.getByRole("button", { name: "New Game" }).click();
  await expect(page).toHaveURL(/\/games\/\d+$/);
  await expect(page.getByText("Player X: play in any open board.")).toBeVisible();
}

test("the professor's example: your cell picks your opponent's board", async ({ page }) => {
  await startNewGame(page);

  // X plays the center cell (5) of board C -> O must play in board E.
  await play(page, 2, 4);
  await expect(page.getByText("Player O: play in board E.")).toBeVisible();
  const enabledCells = page.locator("button[aria-label^='Board']:not([disabled])");
  await expect(enabledCells).toHaveCount(9);

  // O plays the lower-right cell (9) of board E -> X must play in board I.
  await play(page, 4, 8);
  await expect(page.getByText("Player X: play in board I.")).toBeVisible();

  // Refreshing the page keeps the game: it is saved on the server.
  await page.reload();
  await expect(page.getByRole("button", { name: "Board C, cell 5, X" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Board E, cell 9, O" })).toBeVisible();
  await expect(page.getByText("Player X: play in board I.")).toBeVisible();
});

test("a full game can be won", async ({ page }) => {
  await startNewGame(page);

  // X wins boards A, B, and C (the top row). Same sequence the backend tests use.
  // prettier-ignore
  const moves: [number, number][] = [
    [0, 3], [3, 0], [0, 4], [4, 0], [0, 5],
    [5, 1], [1, 3], [3, 1], [1, 4], [4, 1], [1, 5],
    [5, 2], [2, 3], [3, 2], [2, 4], [4, 2], [2, 5],
  ];
  for (const [board, cell] of moves) await play(page, board, cell);

  await expect(page.getByText("Player X wins!")).toBeVisible();
  await expect(page.getByText("Won by X")).toHaveCount(3);
  await expect(page.locator("button[aria-label^='Board']:not([disabled])")).toHaveCount(0);

  // And a new game can be started afterwards.
  await page.getByRole("button", { name: "New Game" }).click();
  await expect(page.getByText("Player X: play in any open board.")).toBeVisible();
});
