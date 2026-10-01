"""Ultimate Tic-Tac-Toe rules, as pure functions.

"Pure" means: no database, no HTTP, no clock, no randomness. The same moves
always produce the same state. That makes every rule easy to test on its own.

Numbering (0-8, row by row) is used for both boards and cells:

    0 | 1 | 2        A | B | C   <- the professor's board names
    3 | 4 | 5        D | E | F
    6 | 7 | 8        G | H | I    cells are named 1-9 in the same order

The placement rule (DECISIONS.md, D2):
  * X moves first, anywhere.
  * The CELL you play decides the BOARD your opponent must play in next.
    Example: a move in cell 4 (the center cell) of any board sends the
    opponent to board 4 (E, the center board).
  * If that board is already decided (won or full), the opponent may play
    in any open cell of any undecided board instead.
"""

from collections.abc import Iterable
from dataclasses import dataclass

from app.core.errors import (
    BoardDecidedError,
    BoardNotPlayableError,
    CellOccupiedError,
    GameOverError,
)
from app.models.enums import BoardStatus, GameStatus, Player

BOARD_LABELS = "ABCDEFGHI"

# The 8 ways to get three in a row on any 3x3 grid (used for small boards AND the big board).
WIN_LINES: tuple[tuple[int, int, int], ...] = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
)  # fmt: skip

_WON_BY = {Player.X: BoardStatus.X_WON, Player.O: BoardStatus.O_WON}
_GAME_WON_BY = {Player.X: GameStatus.X_WON, Player.O: GameStatus.O_WON}

type SmallBoard = tuple[Player | None, ...]  # 9 cells


@dataclass(frozen=True)
class Move:
    board: int
    cell: int

    def __post_init__(self) -> None:
        # The API's schema rejects out-of-range numbers with a 422 before they get
        # here; this guard catches programming mistakes elsewhere.
        if not (0 <= self.board <= 8 and 0 <= self.cell <= 8):
            raise ValueError(f"board and cell must be 0-8, got {self.board}, {self.cell}")


@dataclass(frozen=True)
class GameState:
    """Everything about a game that can be worked out from its moves."""

    cells: tuple[SmallBoard, ...]  # cells[board][cell]
    board_statuses: tuple[BoardStatus, ...]
    status: GameStatus
    current_player: Player | None  # None once the game is over
    forced_board: int | None  # None means a free move (any undecided board)
    playable_boards: tuple[int, ...]
    move_count: int


def small_board_result(cells: SmallBoard) -> BoardStatus:
    """Won if someone has three in a row; a draw if full with no winner; otherwise open."""
    for a, b, c in WIN_LINES:
        mark = cells[a]
        if mark is not None and mark == cells[b] == cells[c]:
            return _WON_BY[mark]
    if all(cell is not None for cell in cells):
        return BoardStatus.DRAW
    return BoardStatus.OPEN


def game_result(board_statuses: tuple[BoardStatus, ...]) -> GameStatus:
    """Three WON small boards in a row wins. Drawn boards never count toward a line.

    The game is a draw only when all nine boards are decided and nobody has a line.
    """
    for player, won in _WON_BY.items():
        for a, b, c in WIN_LINES:
            if board_statuses[a] == board_statuses[b] == board_statuses[c] == won:
                return _GAME_WON_BY[player]
    if all(status is not BoardStatus.OPEN for status in board_statuses):
        return GameStatus.DRAW
    return GameStatus.IN_PROGRESS


def initial_state() -> GameState:
    return GameState(
        cells=tuple((None,) * 9 for _ in range(9)),
        board_statuses=(BoardStatus.OPEN,) * 9,
        status=GameStatus.IN_PROGRESS,
        current_player=Player.X,
        forced_board=None,
        playable_boards=tuple(range(9)),
        move_count=0,
    )


def apply_move(state: GameState, move: Move) -> GameState:
    """Return the state after `move`, or raise a RuleViolationError if it is illegal."""
    _validate(state, move)
    player = state.current_player
    assert player is not None  # _validate refuses moves once the game is over

    # Place the mark (tuples are immutable, so build new ones).
    new_board = tuple(
        player if i == move.cell else mark for i, mark in enumerate(state.cells[move.board])
    )
    cells = tuple(new_board if b == move.board else board for b, board in enumerate(state.cells))
    board_statuses = tuple(
        small_board_result(new_board) if b == move.board else status
        for b, status in enumerate(state.board_statuses)
    )
    status = game_result(board_statuses)

    if status is not GameStatus.IN_PROGRESS:
        return GameState(
            cells=cells,
            board_statuses=board_statuses,
            status=status,
            current_player=None,
            forced_board=None,
            playable_boards=(),
            move_count=state.move_count + 1,
        )

    # The cell just played picks the next board, unless that board is decided.
    # (This is checked AFTER updating statuses, so a move that just closed the
    # board it points to also gives a free move.)
    target = move.cell
    forced_board = target if board_statuses[target] is BoardStatus.OPEN else None
    if forced_board is not None:
        playable: tuple[int, ...] = (forced_board,)
    else:
        playable = tuple(b for b, s in enumerate(board_statuses) if s is BoardStatus.OPEN)

    return GameState(
        cells=cells,
        board_statuses=board_statuses,
        status=status,
        current_player=player.opponent,
        forced_board=forced_board,
        playable_boards=playable,
        move_count=state.move_count + 1,
    )


def replay(moves: Iterable[Move]) -> GameState:
    """Rebuild a game from its moves in order. Players alternate starting with X."""
    state = initial_state()
    for move in moves:
        state = apply_move(state, move)
    return state


def _validate(state: GameState, move: Move) -> None:
    if state.status is not GameStatus.IN_PROGRESS:
        raise GameOverError("The game is over. Start a new game to keep playing.")

    board_name = BOARD_LABELS[move.board]
    if state.forced_board is not None and move.board != state.forced_board:
        raise BoardNotPlayableError(
            f"You must play in board {BOARD_LABELS[state.forced_board]}, not board {board_name}."
        )
    if state.board_statuses[move.board] is not BoardStatus.OPEN:
        raise BoardDecidedError(f"Board {board_name} is already decided. Choose an open board.")
    if state.cells[move.board][move.cell] is not None:
        raise CellOccupiedError(f"Cell {move.cell + 1} of board {board_name} is already taken.")
