// The app's URLs. Shared by main.tsx (browser) and the tests (memory router).
import type { RouteObject } from "react-router";

import { GamePage } from "./GamePage";
import { HomePage } from "./HomePage";
import { NotFoundPage } from "./NotFoundPage";

export const routes: RouteObject[] = [
  { path: "/", element: <HomePage /> },
  // The game id is in the URL, so refreshing the page keeps the game (A1).
  { path: "/games/:gameId", element: <GamePage /> },
  { path: "*", element: <NotFoundPage /> },
];
