# Ultimate Tic-Tac-Toe (COSC 410 warmup)

Two players, X and O, share one computer and play Ultimate Tic-Tac-Toe: a 3x3 grid of
small tic-tac-toe boards. The cell you play decides which board your opponent must play in next.

**Status:** under construction. The game itself is not built yet.

## Run it

Requires Docker Desktop, running.

```
docker compose up --build
```

Then open http://localhost:8080. Stop with Control + C, then `docker compose down`.

The original plain-JavaScript prototype is preserved at the git tag `prototype-vanilla-js`.
See `DECISIONS.md` for the design choices and the assumptions made about the requirements.
