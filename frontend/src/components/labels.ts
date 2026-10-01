// Display text only. The API numbers boards and cells 0-8; players see the
// professor's names: boards A-I and cells 1-9 (DECISIONS.md, A16).
import type { Game, Player } from "../api/client";

export const boardLabel = (index: number): string => "ABCDEFGHI"[index];
export const cellLabel = (index: number): string => String(index + 1);
export const playerLabel = (player: Player): string => player.toUpperCase();

/** The one-line status shown above the board. It reads state; it decides nothing. */
export function statusMessage(game: Game): string {
  switch (game.status) {
    case "x_won":
      return "Player X wins!";
    case "o_won":
      return "Player O wins!";
    case "draw":
      return "It's a draw. Every board is decided and nobody has three in a row.";
    case "in_progress": {
      const player = game.current_player === null ? "" : playerLabel(game.current_player);
      return game.forced_board === null
        ? `Player ${player}: play in any open board.`
        : `Player ${player}: play in board ${boardLabel(game.forced_board)}.`;
    }
  }
}
