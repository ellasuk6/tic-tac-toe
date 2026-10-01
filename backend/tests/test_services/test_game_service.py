"""Service tests: the glue between rules and storage (transactions, not-found, conflicts)."""

import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from app.core import database
from app.core.errors import CellOccupiedError, GameNotFoundError, MoveConflictError
from app.models.enums import GameStatus, Player
from app.models.game import Move
from app.repositories import game_repository as repo
from app.services import game_service
from tests.game_sequences import X_WINS_TOP_ROW


def count_moves(engine: Engine) -> int:
    # A separate session sees only what was committed.
    with Session(engine) as other:
        return other.scalar(select(func.count()).select_from(Move)) or 0


def test_create_game_is_committed(session: Session, db_engine: Engine) -> None:
    view = game_service.create_game(session)

    with Session(db_engine) as other:
        assert repo.get_game(other, view.game.id) is not None
    assert view.state.current_player is Player.X


def test_get_game_raises_not_found(session: Session) -> None:
    with pytest.raises(GameNotFoundError) as excinfo:
        game_service.get_game(session, 999)

    assert excinfo.value.code == "game_not_found"


def test_play_move_saves_moves_in_order(session: Session, db_engine: Engine) -> None:
    game_id = game_service.create_game(session).game.id

    game_service.play_move(session, game_id, board=2, cell=4)
    game_service.play_move(session, game_id, board=4, cell=8)

    assert count_moves(db_engine) == 2
    moves = repo.list_moves(session, game_id)
    assert [(m.seq, m.board, m.cell) for m in moves] == [(0, 2, 4), (1, 4, 8)]


def test_get_game_replays_the_stored_moves(session: Session) -> None:
    game_id = game_service.create_game(session).game.id
    for board, cell in X_WINS_TOP_ROW:
        game_service.play_move(session, game_id, board, cell)

    view = game_service.get_game(session, game_id)

    assert view.state.status is GameStatus.X_WON
    assert view.state.move_count == len(X_WINS_TOP_ROW)


def test_refused_move_saves_nothing(session: Session, db_engine: Engine) -> None:
    game_id = game_service.create_game(session).game.id
    game_service.play_move(session, game_id, board=0, cell=0)

    with pytest.raises(CellOccupiedError):
        game_service.play_move(session, game_id, board=0, cell=0)

    assert count_moves(db_engine) == 1


def test_simultaneous_moves_keep_only_one(
    session: Session, db_engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Simulate a double click: the second request read the moves BEFORE the first
    # one was saved, so both try to store move number 0.
    game_id = game_service.create_game(session).game.id
    game_service.play_move(session, game_id, board=0, cell=0)
    monkeypatch.setattr(repo, "list_moves", lambda _session, _game_id: [])

    with pytest.raises(MoveConflictError) as excinfo:
        game_service.play_move(session, game_id, board=4, cell=4)

    assert excinfo.value.code == "move_conflict"
    assert count_moves(db_engine) == 1


def test_get_session_yields_a_session_and_closes_it(monkeypatch: pytest.MonkeyPatch) -> None:
    closed: list[bool] = []
    monkeypatch.setattr(Session, "close", lambda self: closed.append(True))

    dependency = database.get_session()
    session = next(dependency)
    assert isinstance(session, Session)
    dependency.close()  # what FastAPI does when the request finishes

    assert closed == [True]
