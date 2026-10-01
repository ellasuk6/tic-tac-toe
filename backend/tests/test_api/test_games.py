"""API tests for /api/v1/games: every endpoint's success shape and each error it can return."""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from httpx import AsyncClient, Response
from sqlalchemy import Engine, event, inspect

from tests.game_sequences import DRAW_BOARD_A, X_WINS_BOARD_A, X_WINS_TOP_ROW

pytestmark = pytest.mark.anyio

GAMES = "/api/v1/games"


async def new_game(client: AsyncClient) -> int:
    response = await client.post(GAMES)
    assert response.status_code == 201
    game_id: int = response.json()["id"]
    return game_id


async def play(client: AsyncClient, game_id: int, board: int, cell: int) -> Response:
    return await client.post(f"{GAMES}/{game_id}/moves", json={"board": board, "cell": cell})


async def play_all(client: AsyncClient, game_id: int, moves: list[tuple[int, int]]) -> None:
    for board, cell in moves:
        response = await play(client, game_id, board, cell)
        assert response.status_code == 201, response.json()


def assert_error(response: Response, status_code: int, code: str) -> None:
    assert response.status_code == status_code
    body = response.json()
    assert set(body) == {"code", "detail"}
    assert body["code"] == code
    assert isinstance(body["detail"], str) and body["detail"]


# --- POST /games ----------------------------------------------------------------------


async def test_create_game_returns_201_location_and_a_fresh_board(client: AsyncClient) -> None:
    response = await client.post(GAMES)

    assert response.status_code == 201
    body = response.json()
    assert response.headers["Location"] == f"{GAMES}/{body['id']}"
    assert body["status"] == "in_progress"
    assert body["current_player"] == "x"
    assert body["forced_board"] is None
    assert body["playable_boards"] == list(range(9))
    assert body["move_count"] == 0
    assert [b["index"] for b in body["boards"]] == list(range(9))
    assert all(b["status"] == "open" and b["cells"] == [None] * 9 for b in body["boards"])


async def test_created_at_is_iso_8601_utc(client: AsyncClient) -> None:
    body = (await client.post(GAMES)).json()

    created_at = datetime.fromisoformat(body["created_at"])

    assert created_at.utcoffset() == timedelta(0)
    assert abs(datetime.now(UTC) - created_at) < timedelta(seconds=5)


async def test_each_new_game_gets_its_own_id(client: AsyncClient) -> None:
    assert await new_game(client) != await new_game(client)


# --- GET /games/{id} ------------------------------------------------------------------


async def test_get_game_returns_the_saved_state(client: AsyncClient) -> None:
    game_id = await new_game(client)
    await play_all(client, game_id, [(2, 4), (4, 8)])

    response = await client.get(f"{GAMES}/{game_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == game_id
    assert body["move_count"] == 2
    assert body["boards"][2]["cells"][4] == "x"
    assert body["boards"][4]["cells"][8] == "o"
    assert body["current_player"] == "x"
    assert body["forced_board"] == 8


async def test_get_missing_game_returns_404(client: AsyncClient) -> None:
    assert_error(await client.get(f"{GAMES}/999"), 404, "game_not_found")


async def test_get_game_with_a_non_numeric_id_returns_422(client: AsyncClient) -> None:
    assert_error(await client.get(f"{GAMES}/abc"), 422, "validation_error")


# --- POST /games/{id}/moves: success --------------------------------------------------


async def test_play_move_returns_201_location_and_the_new_state(client: AsyncClient) -> None:
    game_id = await new_game(client)

    response = await play(client, game_id, board=2, cell=4)  # board C, cell 5

    assert response.status_code == 201
    assert response.headers["Location"] == f"{GAMES}/{game_id}"
    body = response.json()
    assert body["boards"][2]["cells"][4] == "x"
    assert body["current_player"] == "o"
    assert body["forced_board"] == 4  # board E, per the professor's example
    assert body["playable_boards"] == [4]
    assert body["move_count"] == 1


async def test_sent_to_a_decided_board_the_response_shows_a_free_move(
    client: AsyncClient,
) -> None:
    game_id = await new_game(client)
    await play_all(client, game_id, X_WINS_BOARD_A)

    body = (await play(client, game_id, board=5, cell=0)).json()

    assert body["boards"][0]["status"] == "x_won"
    assert body["forced_board"] is None
    assert body["playable_boards"] == [1, 2, 3, 4, 5, 6, 7, 8]


async def test_a_full_game_can_be_won_through_the_api(client: AsyncClient) -> None:
    game_id = await new_game(client)

    await play_all(client, game_id, X_WINS_TOP_ROW)

    body = (await client.get(f"{GAMES}/{game_id}")).json()
    assert body["status"] == "x_won"
    assert body["current_player"] is None
    assert body["playable_boards"] == []


async def test_a_drawn_small_board_is_reported(client: AsyncClient) -> None:
    game_id = await new_game(client)

    await play_all(client, game_id, DRAW_BOARD_A)

    body = (await client.get(f"{GAMES}/{game_id}")).json()
    assert body["boards"][0]["status"] == "draw"
    assert body["status"] == "in_progress"


# --- POST /games/{id}/moves: errors ---------------------------------------------------


async def test_move_in_a_missing_game_returns_404(client: AsyncClient) -> None:
    assert_error(await play(client, 999, 0, 0), 404, "game_not_found")


async def test_move_outside_the_forced_board_returns_409(client: AsyncClient) -> None:
    game_id = await new_game(client)
    await play(client, game_id, 2, 4)  # O must play in board E

    response = await play(client, game_id, 5, 0)

    assert_error(response, 409, "board_not_playable")
    assert "board E" in response.json()["detail"]


async def test_move_on_a_taken_cell_returns_409(client: AsyncClient) -> None:
    game_id = await new_game(client)
    await play(client, game_id, 0, 0)  # sends O to board A

    assert_error(await play(client, game_id, 0, 0), 409, "cell_occupied")


async def test_free_move_into_a_decided_board_returns_409(client: AsyncClient) -> None:
    game_id = await new_game(client)
    await play_all(client, game_id, [*X_WINS_BOARD_A, (5, 0)])  # X is free; board A is won

    assert_error(await play(client, game_id, 0, 0), 409, "board_decided")


async def test_move_after_the_game_is_over_returns_409(client: AsyncClient) -> None:
    game_id = await new_game(client)
    await play_all(client, game_id, X_WINS_TOP_ROW)

    assert_error(await play(client, game_id, 8, 8), 409, "game_over")


async def test_refused_move_is_not_saved(client: AsyncClient) -> None:
    game_id = await new_game(client)
    await play(client, game_id, 0, 0)
    await play(client, game_id, 0, 0)  # refused: cell occupied

    body = (await client.get(f"{GAMES}/{game_id}")).json()
    assert body["move_count"] == 1


@pytest.mark.parametrize(
    "payload",
    [
        {"board": 9, "cell": 0},
        {"board": 0, "cell": -1},
        {"board": 0},
        {"board": "A", "cell": 0},
        {},
    ],
)
async def test_invalid_move_body_returns_422(client: AsyncClient, payload: Any) -> None:
    game_id = await new_game(client)

    response = await client.post(f"{GAMES}/{game_id}/moves", json=payload)

    assert_error(response, 422, "validation_error")


async def test_422_detail_names_the_bad_field(client: AsyncClient) -> None:
    game_id = await new_game(client)

    response = await client.post(f"{GAMES}/{game_id}/moves", json={"board": 9, "cell": 0})

    assert response.json()["detail"].startswith("board:")


# --- Framework errors use the same envelope -------------------------------------------


async def test_unknown_url_returns_404_envelope(client: AsyncClient) -> None:
    assert_error(await client.get("/api/v1/nope"), 404, "not_found")


async def test_wrong_method_returns_405_envelope(client: AsyncClient) -> None:
    assert_error(await client.delete(f"{GAMES}/1"), 405, "method_not_allowed")


# --- Derived values are computed, never stored ----------------------------------------


def test_only_moves_are_stored_not_game_state(db_engine: Engine) -> None:
    inspector = inspect(db_engine)

    game_columns = {c["name"] for c in inspector.get_columns("games")}
    move_columns = {c["name"] for c in inspector.get_columns("moves")}

    assert game_columns == {"id", "created_at"}
    assert move_columns == {"id", "game_id", "seq", "board", "cell", "created_at"}


async def test_reading_a_game_computes_its_state_without_writing(
    client: AsyncClient, db_engine: Engine
) -> None:
    game_id = await new_game(client)
    await play_all(client, game_id, X_WINS_TOP_ROW)
    statements: list[str] = []

    def record(*args: Any) -> None:
        statements.append(str(args[2]).lstrip().upper())

    event.listen(db_engine, "before_cursor_execute", record)
    try:
        body = (await client.get(f"{GAMES}/{game_id}")).json()
    finally:
        event.remove(db_engine, "before_cursor_execute", record)

    assert body["status"] == "x_won"  # computed from the 17 stored moves...
    assert statements  # ...which were read from the database...
    assert all(s.startswith("SELECT") for s in statements)  # ...with no write at all
