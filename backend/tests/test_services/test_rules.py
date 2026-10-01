"""Tests for the pure rules engine (app/services/rules.py).

Boards and cells are numbered 0-8, row by row. The professor names boards A-I
and cells 1-9, so "board C, cell 5" is Move(board=2, cell=4).
"""

import pytest

from app.core.errors import (
    BoardDecidedError,
    BoardNotPlayableError,
    CellOccupiedError,
    GameOverError,
)
from app.models.enums import BoardStatus, GameStatus, Player
from app.services.rules import (
    WIN_LINES,
    GameState,
    Move,
    apply_move,
    game_result,
    initial_state,
    replay,
    small_board_result,
)
from tests.game_sequences import DRAW_BOARD_A, X_WINS_BOARD_A, X_WINS_TOP_ROW

X, O, _ = Player.X, Player.O, None  # noqa: E741  (short names keep board literals readable)
OPEN, XW, OW, DRAW = BoardStatus.OPEN, BoardStatus.X_WON, BoardStatus.O_WON, BoardStatus.DRAW


def play(*moves: tuple[int, int]) -> GameState:
    """Replay (board, cell) pairs from a new game."""
    return replay(Move(board, cell) for board, cell in moves)


# --- Starting position ---------------------------------------------------------------


def test_new_game_x_moves_first_and_may_play_any_board() -> None:
    state = initial_state()

    assert state.current_player is X
    assert state.forced_board is None
    assert state.playable_boards == tuple(range(9))
    assert state.status is GameStatus.IN_PROGRESS
    assert state.move_count == 0
    assert all(status is OPEN for status in state.board_statuses)


@pytest.mark.parametrize("board", range(9))
def test_first_move_is_allowed_in_any_board(board: int) -> None:
    state = play((board, 1))

    assert state.cells[board][1] is X


def test_players_alternate() -> None:
    state = initial_state()
    for expected, move in zip([X, O, X], [(0, 1), (1, 2), (2, 3)], strict=True):
        assert state.current_player is expected
        state = apply_move(state, Move(*move))

    assert state.current_player is O
    assert state.move_count == 3


# --- The placement rule: your cell picks the opponent's board ---------------------


@pytest.mark.parametrize("cell", range(9))
def test_cell_played_sends_opponent_to_matching_board(cell: int) -> None:
    state = play((8, cell))

    assert state.forced_board == cell
    assert state.playable_boards == (cell,)


def test_professor_example_center_cell_sends_opponent_to_center_board() -> None:
    # "X decides to play in the center square (5)" of board C -> O must play in board E.
    state = play((2, 4))

    assert state.forced_board == 4  # board E


def test_professor_example_lower_left_cell_sends_opponent_to_board_g() -> None:
    # "X wanted to play in the lower left square (7)" of board C -> O must play in board G.
    state = play((2, 6))

    assert state.forced_board == 6  # board G


def test_forced_player_may_play_any_open_cell_in_the_forced_board() -> None:
    state = play((2, 4), (4, 8))

    assert state.cells[4][8] is O


def test_forced_player_is_refused_outside_the_forced_board() -> None:
    state = play((2, 4))  # O must play in board E

    with pytest.raises(BoardNotPlayableError) as excinfo:
        apply_move(state, Move(board=5, cell=0))

    assert excinfo.value.code == "board_not_playable"
    assert "board E" in excinfo.value.detail


# --- Occupied cells -------------------------------------------------------------------


def test_occupied_cell_is_refused() -> None:
    state = play((0, 0))  # X takes A1 and sends O to board A

    with pytest.raises(CellOccupiedError) as excinfo:
        apply_move(state, Move(board=0, cell=0))

    assert excinfo.value.code == "cell_occupied"


def test_refused_move_changes_nothing() -> None:
    state = play((0, 0))

    with pytest.raises(CellOccupiedError):
        apply_move(state, Move(board=0, cell=0))

    assert state == play((0, 0))


# --- Small boards ---------------------------------------------------------------------


@pytest.mark.parametrize("line", WIN_LINES)
@pytest.mark.parametrize(("player", "expected"), [(X, XW), (O, OW)])
def test_three_in_a_row_wins_a_small_board(
    line: tuple[int, int, int], player: Player, expected: BoardStatus
) -> None:
    cells = tuple(player if i in line else None for i in range(9))

    assert small_board_result(cells) is expected


def test_full_small_board_with_no_line_is_a_draw() -> None:
    assert small_board_result((X, O, X, X, O, O, O, X, X)) is DRAW


def test_small_board_with_no_line_and_empty_cells_is_open() -> None:
    assert small_board_result((X, O, X, X, O, O, O, X, _)) is OPEN


def test_completing_a_line_in_play_marks_the_board_won() -> None:
    state = play(*X_WINS_BOARD_A)

    assert state.board_statuses[0] is XW
    assert state.status is GameStatus.IN_PROGRESS


def test_won_board_refuses_further_moves() -> None:
    # After X wins board A, O is sent to board F (cell 5). O plays F1, which would
    # send X to board A, but A is decided, so X moves freely. X still may not pick A.
    state = play(*X_WINS_BOARD_A, (5, 0))

    with pytest.raises(BoardDecidedError) as excinfo:
        apply_move(state, Move(board=0, cell=0))

    assert excinfo.value.code == "board_decided"


def test_filling_a_board_with_no_line_marks_it_drawn() -> None:
    state = play(*DRAW_BOARD_A)

    assert state.board_statuses[0] is DRAW
    assert state.cells[0] == (X, O, X, X, O, O, O, X, X)


def test_drawn_board_refuses_further_moves() -> None:
    state = play(*DRAW_BOARD_A)

    with pytest.raises(BoardDecidedError) as excinfo:
        apply_move(state, Move(board=0, cell=0))

    assert excinfo.value.code == "board_decided"


# --- Being sent to a decided board gives a free move ----------------------------------


def test_sent_to_a_won_board_gives_a_free_move() -> None:
    state = play(*X_WINS_BOARD_A, (5, 0))  # O's cell 0 points at board A, which X won

    assert state.current_player is X
    assert state.forced_board is None
    assert state.playable_boards == (1, 2, 3, 4, 5, 6, 7, 8)  # every board except A


def test_sent_to_a_drawn_board_gives_a_free_move() -> None:
    state = play(*DRAW_BOARD_A)  # X's last cell (0) points at board A, now drawn

    assert state.current_player is O
    assert state.forced_board is None
    assert state.playable_boards == (1, 2, 3, 4, 5, 6, 7, 8)


def test_free_move_is_allowed_in_any_open_board() -> None:
    state = play(*X_WINS_BOARD_A, (5, 0))

    state = apply_move(state, Move(board=8, cell=8))

    assert state.cells[8][8] is X


# --- The big board --------------------------------------------------------------------


@pytest.mark.parametrize("line", WIN_LINES)
def test_three_won_boards_in_a_row_win_the_game(line: tuple[int, int, int]) -> None:
    statuses = tuple(XW if i in line else OPEN for i in range(9))

    assert game_result(statuses) is GameStatus.X_WON


def test_o_can_win_the_game() -> None:
    statuses = (OW, OW, OW, OPEN, OPEN, OPEN, OPEN, OPEN, OPEN)

    assert game_result(statuses) is GameStatus.O_WON


def test_drawn_boards_never_count_toward_a_line() -> None:
    assert game_result((DRAW, DRAW, DRAW, OPEN, OPEN, OPEN, OPEN, OPEN, OPEN)) is (
        GameStatus.IN_PROGRESS
    )
    assert game_result((XW, XW, DRAW, OPEN, OPEN, OPEN, OPEN, OPEN, OPEN)) is (
        GameStatus.IN_PROGRESS
    )


def test_mixed_line_does_not_win() -> None:
    statuses = (XW, OW, XW, OPEN, OPEN, OPEN, OPEN, OPEN, OPEN)

    assert game_result(statuses) is GameStatus.IN_PROGRESS


def test_all_boards_decided_with_no_line_is_a_game_draw() -> None:
    statuses = (XW, OW, XW, XW, OW, OW, OW, XW, DRAW)

    assert game_result(statuses) is GameStatus.DRAW


def test_game_is_not_a_draw_while_any_board_is_open() -> None:
    # Nobody can still make a line here, but A6 says: draw only when all 9 are decided.
    statuses = (XW, OW, XW, XW, OW, OW, OW, XW, OPEN)

    assert game_result(statuses) is GameStatus.IN_PROGRESS


def test_line_wins_even_when_every_board_is_decided() -> None:
    statuses = (XW, XW, XW, OW, OW, DRAW, OW, DRAW, DRAW)

    assert game_result(statuses) is GameStatus.X_WON


# --- Game over ------------------------------------------------------------------------


def test_winning_three_boards_in_play_ends_the_game() -> None:
    state = play(*X_WINS_TOP_ROW)

    assert state.status is GameStatus.X_WON
    assert state.board_statuses[:3] == (XW, XW, XW)
    assert state.current_player is None
    assert state.forced_board is None
    assert state.playable_boards == ()


def test_no_move_is_allowed_after_the_game_ends() -> None:
    state = play(*X_WINS_TOP_ROW)

    with pytest.raises(GameOverError) as excinfo:
        apply_move(state, Move(board=8, cell=8))

    assert excinfo.value.code == "game_over"


def test_move_before_the_game_ends_is_allowed() -> None:
    state = play(*X_WINS_TOP_ROW[:-1])  # one move short of X's win

    state = apply_move(state, Move(board=2, cell=5))

    assert state.status is GameStatus.X_WON


# --- Moves and replay -----------------------------------------------------------------


@pytest.mark.parametrize(("board", "cell"), [(-1, 0), (9, 0), (0, -1), (0, 9)])
def test_move_outside_0_to_8_is_rejected(board: int, cell: int) -> None:
    with pytest.raises(ValueError, match="must be 0-8"):
        Move(board, cell)


def test_replay_matches_applying_moves_one_at_a_time() -> None:
    state = initial_state()
    for board, cell in X_WINS_BOARD_A:
        state = apply_move(state, Move(board, cell))

    assert replay(Move(b, c) for b, c in X_WINS_BOARD_A) == state


def test_replay_stops_at_the_first_illegal_move() -> None:
    with pytest.raises(BoardNotPlayableError):
        play((2, 4), (5, 0))  # O was sent to board E, not F
