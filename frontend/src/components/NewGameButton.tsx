import { useNavigate } from "react-router";

import { useCreateGame } from "../api/queries";

/** Starts a game on the server, then opens its page (/games/:id). */
export function NewGameButton() {
  const navigate = useNavigate();
  const createGame = useCreateGame();

  const start = () => {
    createGame.mutate(undefined, {
      onSuccess: (game) => navigate(`/games/${game.id}`),
    });
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <button
        type="button"
        onClick={start}
        disabled={createGame.isPending}
        className="rounded-md bg-ink px-5 py-2 font-semibold text-paper enabled:cursor-pointer enabled:hover:bg-ink/85 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ink disabled:opacity-60"
      >
        {createGame.isPending ? "Starting…" : "New Game"}
      </button>
      {createGame.isError && (
        <p role="alert" className="text-sm text-o">
          Could not start a game: {createGame.error.message} Try again.
        </p>
      )}
    </div>
  );
}
