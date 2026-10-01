"""Data access for games and moves.

Repositories only read and write rows. They contain no game rules and know
nothing about HTTP. They `flush` (so new rows get ids) but never `commit`:
the service decides when a unit of work is finished.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.game import Game, Move


def create_game(session: Session) -> Game:
    game = Game()
    session.add(game)
    session.flush()
    return game


def get_game(session: Session, game_id: int) -> Game | None:
    return session.get(Game, game_id)


def list_moves(session: Session, game_id: int) -> list[Move]:
    """All moves of a game, oldest first."""
    statement = select(Move).where(Move.game_id == game_id).order_by(Move.seq)
    return list(session.scalars(statement))


def add_move(session: Session, game_id: int, seq: int, board: int, cell: int) -> Move:
    move = Move(game_id=game_id, seq=seq, board=board, cell=cell)
    session.add(move)
    session.flush()
    return move
