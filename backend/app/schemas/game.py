"""Request and response shapes for the games API.

These classes are the contract with the frontend: FastAPI publishes them in the
OpenAPI schema, and the frontend generates its TypeScript types from that.
"""

from datetime import datetime
from typing import Annotated, Self

from pydantic import BaseModel, Field

from app.models.enums import BoardStatus, GameStatus, Player
from app.services.game_service import GameView

# Boards and cells are numbered 0-8, row by row (A-I and 1-9 in the UI).
Index = Annotated[int, Field(ge=0, le=8)]


class SmallBoardOut(BaseModel):
    index: Index
    status: BoardStatus
    cells: list[Player | None] = Field(min_length=9, max_length=9)


class GameOut(BaseModel):
    id: int
    created_at: datetime
    status: GameStatus
    current_player: Player | None = Field(
        description="Whose turn it is; null once the game is over."
    )
    forced_board: Index | None = Field(
        description="The board the current player must play in; null means a free move."
    )
    playable_boards: list[Index]
    move_count: int
    boards: list[SmallBoardOut] = Field(min_length=9, max_length=9)

    @classmethod
    def from_view(cls, view: GameView) -> Self:
        state = view.state
        return cls(
            id=view.game.id,
            created_at=view.game.created_at,
            status=state.status,
            current_player=state.current_player,
            forced_board=state.forced_board,
            playable_boards=list(state.playable_boards),
            move_count=state.move_count,
            boards=[
                SmallBoardOut(index=i, status=status, cells=list(state.cells[i]))
                for i, status in enumerate(state.board_statuses)
            ],
        )


class MoveIn(BaseModel):
    board: Index
    cell: Index


class ErrorOut(BaseModel):
    """The one error shape every endpoint uses."""

    code: str = Field(examples=["cell_occupied"])
    detail: str = Field(examples=["Cell 5 of board E is already taken."])
