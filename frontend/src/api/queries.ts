// TanStack Query hooks: the only way components talk to the server.
// No useEffect-and-setState fetching anywhere (constitution rule).
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createGame, type Game, getGame, playMove } from "./client";

export const gameKey = (gameId: number) => ["games", gameId] as const;

export function useGame(gameId: number) {
  return useQuery({ queryKey: gameKey(gameId), queryFn: () => getGame(gameId) });
}

export function useCreateGame() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createGame,
    // The response already is the new game: cache it so its page shows instantly.
    onSuccess: (game: Game) => queryClient.setQueryData(gameKey(game.id), game),
  });
}

export function usePlayMove(gameId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ board, cell }: { board: number; cell: number }) => playMove(gameId, board, cell),
    // The server answers with the whole updated game, so no refetch is needed.
    onSuccess: (game: Game) => queryClient.setQueryData(gameKey(gameId), game),
  });
}
