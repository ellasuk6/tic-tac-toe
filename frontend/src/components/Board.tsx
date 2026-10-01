// The 3x3 grid of small boards. Pure display: which boards are playable comes
// from the server (`playable_boards`); this file applies no game rules.
import type { Game, Player, SmallBoard } from "../api/client";
import { boardLabel, cellLabel, playerLabel } from "./labels";

type BoardProps = {
  game: Game;
  /** True while a move is being sent, so a double click cannot send two. */
  busy: boolean;
  onPlay: (board: number, cell: number) => void;
};

export function Board({ game, busy, onPlay }: BoardProps) {
  const inProgress = game.status === "in_progress";
  return (
    <div className="grid w-full max-w-xl grid-cols-3 gap-2 rounded-lg bg-ink p-2 sm:gap-3 sm:p-3">
      {game.boards.map((board) => (
        <SmallBoardView
          key={board.index}
          board={board}
          playable={inProgress && game.playable_boards.includes(board.index)}
          busy={busy}
          onPlay={onPlay}
        />
      ))}
    </div>
  );
}

type SmallBoardProps = {
  board: SmallBoard;
  playable: boolean;
  busy: boolean;
  onPlay: (board: number, cell: number) => void;
};

function decidedText(board: SmallBoard): string | null {
  if (board.status === "x_won") return "Won by X";
  if (board.status === "o_won") return "Won by O";
  if (board.status === "draw") return "Draw";
  return null;
}

function SmallBoardView({ board, playable, busy, onPlay }: SmallBoardProps) {
  const label = boardLabel(board.index);
  const decided = decidedText(board);
  return (
    <section
      aria-label={`Board ${label}${decided ? `, ${decided.toLowerCase()}` : ""}`}
      className={`relative rounded-md p-1 ${playable ? "bg-play" : "bg-paper"} ${
        decided ? "opacity-60" : ""
      }`}
    >
      <span aria-hidden="true" className="absolute top-0.5 left-1 text-[0.6rem] text-muted">
        {label}
      </span>
      <div className="grid grid-cols-3 gap-0.5">
        {board.cells.map((mark, cell) => (
          <CellButton
            key={cell}
            boardIndex={board.index}
            cell={cell}
            mark={mark}
            enabled={playable && mark === null && !busy}
            onPlay={onPlay}
          />
        ))}
      </div>
      {decided && (
        <p className="pointer-events-none absolute inset-0 flex items-center justify-center font-display text-lg font-bold text-ink sm:text-2xl">
          {decided}
        </p>
      )}
    </section>
  );
}

type CellProps = {
  boardIndex: number;
  cell: number;
  mark: Player | null;
  enabled: boolean;
  onPlay: (board: number, cell: number) => void;
};

function CellButton({ boardIndex, cell, mark, enabled, onPlay }: CellProps) {
  const contents = mark === null ? "empty" : playerLabel(mark);
  return (
    <button
      type="button"
      aria-label={`Board ${boardLabel(boardIndex)}, cell ${cellLabel(cell)}, ${contents}`}
      disabled={!enabled}
      onClick={() => onPlay(boardIndex, cell)}
      className={`flex aspect-square items-center justify-center rounded-sm bg-white/80 font-display text-lg font-bold sm:text-2xl ${
        mark === "x" ? "text-x" : "text-o"
      } enabled:cursor-pointer enabled:hover:bg-white focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-ink disabled:cursor-default`}
    >
      {mark === null ? "" : playerLabel(mark)}
    </button>
  );
}
