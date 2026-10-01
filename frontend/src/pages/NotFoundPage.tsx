import { Link } from "react-router";

export function NotFoundPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col items-center justify-center gap-4 px-4 text-center">
      <h1 className="font-display text-3xl font-bold">Page not found</h1>
      <Link to="/" className="underline">
        Go to the start page
      </Link>
    </main>
  );
}
