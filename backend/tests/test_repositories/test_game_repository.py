from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.game import Game, Move
from app.repositories import game_repository as repo


def test_create_game_assigns_an_id_and_a_utc_created_at(session: Session) -> None:
    before = datetime.now(UTC)

    game = repo.create_game(session)

    assert game.id is not None
    assert game.created_at.tzinfo is UTC
    assert before - timedelta(seconds=1) <= game.created_at <= datetime.now(UTC)


def test_created_at_is_still_utc_after_a_round_trip(session: Session) -> None:
    game_id = repo.create_game(session).id
    session.commit()
    session.expunge_all()  # force the next read to come from the database

    reloaded = repo.get_game(session, game_id)

    assert reloaded is not None
    assert reloaded.created_at.tzinfo is UTC


def test_get_game_returns_the_game(session: Session) -> None:
    game = repo.create_game(session)

    assert repo.get_game(session, game.id) is game


def test_get_game_returns_none_when_missing(session: Session) -> None:
    assert repo.get_game(session, 999) is None


def test_list_moves_of_a_new_game_is_empty(session: Session) -> None:
    game = repo.create_game(session)

    assert repo.list_moves(session, game.id) == []


def test_list_moves_returns_moves_in_order_regardless_of_insert_order(session: Session) -> None:
    game = repo.create_game(session)
    repo.add_move(session, game.id, seq=1, board=4, cell=0)
    repo.add_move(session, game.id, seq=0, board=0, cell=4)
    repo.add_move(session, game.id, seq=2, board=0, cell=8)

    moves = repo.list_moves(session, game.id)

    assert [(m.seq, m.board, m.cell) for m in moves] == [(0, 0, 4), (1, 4, 0), (2, 0, 8)]


def test_list_moves_only_returns_that_games_moves(session: Session) -> None:
    first = repo.create_game(session)
    second = repo.create_game(session)
    repo.add_move(session, first.id, seq=0, board=0, cell=0)
    repo.add_move(session, second.id, seq=0, board=8, cell=8)

    moves = repo.list_moves(session, second.id)

    assert [(m.board, m.cell) for m in moves] == [(8, 8)]


def test_add_move_stores_a_utc_created_at(session: Session) -> None:
    game = repo.create_game(session)

    move = repo.add_move(session, game.id, seq=0, board=2, cell=4)

    assert move.created_at.tzinfo is UTC


def test_the_same_move_number_cannot_be_stored_twice(session: Session) -> None:
    # This is the database's last line of defence if two requests race to play move 0.
    game = repo.create_game(session)
    repo.add_move(session, game.id, seq=0, board=0, cell=0)

    with pytest.raises(IntegrityError):
        repo.add_move(session, game.id, seq=0, board=1, cell=1)


@pytest.mark.parametrize(
    ("seq", "board", "cell"), [(0, 9, 0), (0, -1, 0), (0, 0, 9), (0, 0, -1), (81, 0, 0)]
)
def test_out_of_range_numbers_are_refused_by_the_database(
    session: Session, seq: int, board: int, cell: int
) -> None:
    game = repo.create_game(session)

    with pytest.raises(IntegrityError):
        repo.add_move(session, game.id, seq=seq, board=board, cell=cell)


def test_a_move_must_belong_to_an_existing_game(session: Session) -> None:
    with pytest.raises(IntegrityError):
        repo.add_move(session, game_id=999, seq=0, board=0, cell=0)


def test_deleting_a_game_deletes_its_moves(session: Session) -> None:
    game = repo.create_game(session)
    repo.add_move(session, game.id, seq=0, board=0, cell=0)
    session.commit()
    session.expire_all()

    session.delete(game)
    session.commit()

    assert session.scalar(select(func.count()).select_from(Move)) == 0
    assert session.scalar(select(func.count()).select_from(Game)) == 0
