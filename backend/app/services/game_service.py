"""Game use cases: create a game, read a game, play a move.

The service connects the pure rules (rules.py) to storage (the repository):
load the moves, replay them to get the current state, let the rules check the
new move, save it, and commit. It knows nothing about HTTP and writes no SQL.
"""

from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import GameNotFoundError, MoveConflictError
from app.models.game import Game
from app.repositories import game_repository as repo
from app.services import rules


@dataclass(frozen=True)
class GameView:
    """A stored game plus the state computed from its moves."""

    game: Game
    state: rules.GameState


def create_game(session: Session) -> GameView:
    game = repo.create_game(session)
    session.commit()
    return GameView(game=game, state=rules.initial_state())


def get_game(session: Session, game_id: int) -> GameView:
    game = _load_game(session, game_id)
    return GameView(game=game, state=_current_state(session, game_id))


def play_move(session: Session, game_id: int, board: int, cell: int) -> GameView:
    game = _load_game(session, game_id)
    state = _current_state(session, game_id)

    # Raises a RuleViolationError (game_over, board_not_playable, ...) if illegal.
    new_state = rules.apply_move(state, rules.Move(board=board, cell=cell))

    try:
        repo.add_move(session, game_id, seq=state.move_count, board=board, cell=cell)
        session.commit()
    except IntegrityError as error:
        # Two requests computed the same move number; the database kept only one.
        session.rollback()
        raise MoveConflictError(
            "Another move was just played in this game. Reload and try again."
        ) from error

    return GameView(game=game, state=new_state)


def _load_game(session: Session, game_id: int) -> Game:
    game = repo.get_game(session, game_id)
    if game is None:
        raise GameNotFoundError(f"Game {game_id} does not exist.")
    return game


def _current_state(session: Session, game_id: int) -> rules.GameState:
    moves = repo.list_moves(session, game_id)
    return rules.replay(rules.Move(board=m.board, cell=m.cell) for m in moves)
