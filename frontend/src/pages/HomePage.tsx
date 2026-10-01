import { NewGameButton } from "../components/NewGameButton";

export function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col items-center justify-center gap-6 px-4 text-center">
      <h1 className="font-display text-4xl font-bold">Ultimate Tic-Tac-Toe</h1>
      <p className="text-muted">
        Two players, one computer. Nine games of tic-tac-toe at once: the cell you play decides
        which board your opponent must play in next. Win three boards in a row to win.
      </p>
      <NewGameButton />
    </main>
  );
}
