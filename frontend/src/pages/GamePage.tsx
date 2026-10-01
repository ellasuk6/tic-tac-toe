import { Link, useParams } from "react-router";

import { ApiError } from "../api/client";
import { useGame, usePlayMove } from "../api/queries";
import { Board } from "../components/Board";
import { statusMessage } from "../components/labels";
import { NewGameButton } from "../components/NewGameButton";

export function GamePage() {
  const { gameId } = useParams();
  const id = Number(gameId);
  // "/games/abc" can never be a game, so skip the request and show "not found".
  if (!Number.isInteger(id) || id < 1) return <GameNotFound />;
  // `key` gives each game its own page state, e.g. clears a move error on New Game.
  return <Game key={id} gameId={id} />;
}

function Game({ gameId }: { gameId: number }) {
  const game = useGame(gameId);
  const playMove = usePlayMove(gameId);

  if (game.isPending) {
    return (
      <Shell>
        <p role="status">Loading game…</p>
      </Shell>
    );
  }

  if (game.isError) {
    if (game.error instanceof ApiError && game.error.status === 404) return <GameNotFound />;
    return (
      <Shell>
        <div role="alert" className="flex flex-col items-center gap-3">
          <p>Could not load the game: {game.error.message}</p>
          <button
            type="button"
            onClick={() => void game.refetch()}
            className="rounded-md border border-ink px-4 py-1.5 font-semibold enabled:cursor-pointer"
          >
            Retry
          </button>
        </div>
      </Shell>
    );
  }

  const data = game.data;
  const over = data.status !== "in_progress";
  return (
    <Shell>
      <p
        role="status"
        aria-live="polite"
        className={`text-center text-lg ${over ? "font-display text-2xl font-bold" : ""}`}
      >
        {statusMessage(data)}
      </p>
      {data.move_count === 0 && (
        <p className="text-center text-sm text-muted">
          New game. X goes first and may play anywhere. Highlighted boards are where the next move
          can go.
        </p>
      )}
      {playMove.isError && (
        <p role="alert" className="text-center text-sm text-o">
          {playMove.error.message}
        </p>
      )}
      <Board
        game={data}
        busy={playMove.isPending}
        onPlay={(board, cell) => playMove.mutate({ board, cell })}
      />
      <NewGameButton />
    </Shell>
  );
}

function GameNotFound() {
  return (
    <Shell>
      <div role="alert" className="flex flex-col items-center gap-3">
        <p>Game not found.</p>
      </div>
      <NewGameButton />
    </Shell>
  );
}

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col items-center gap-4 px-4 py-6">
      <h1 className="font-display text-3xl font-bold">
        <Link to="/" className="hover:underline">
          Ultimate Tic-Tac-Toe
        </Link>
      </h1>
      {children}
    </main>
  );
}
