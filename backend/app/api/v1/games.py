"""Games endpoints. Routers only translate HTTP <-> service calls: no game rules here."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.schemas.game import ErrorOut, GameOut, MoveIn
from app.services import game_service

router = APIRouter(prefix="/games", tags=["games"])

SessionDep = Annotated[Session, Depends(get_session)]

# Extra responses listed in the OpenAPI docs (FastAPI's expected type for `responses=`).
Responses = dict[int | str, dict[str, Any]]

NOT_FOUND: Responses = {
    404: {"model": ErrorOut, "description": "No game with this id (`game_not_found`)."}
}
RULE_REFUSED: Responses = {
    409: {
        "model": ErrorOut,
        "description": "A game rule refused the move: `game_over`, `board_not_playable`, "
        "`board_decided`, `cell_occupied`, or `move_conflict`.",
    }
}
INVALID: Responses = {422: {"model": ErrorOut, "description": "The request failed validation."}}


def _game_location(game_id: int) -> str:
    return f"/api/v1/games/{game_id}"


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=GameOut,
    summary="Start a new game",
)
def create_game(session: SessionDep, response: Response) -> GameOut:
    view = game_service.create_game(session)
    response.headers["Location"] = _game_location(view.game.id)
    return GameOut.from_view(view)


@router.get(
    "/{game_id}",
    response_model=GameOut,
    responses={**NOT_FOUND, **INVALID},
    summary="Get a game's current state",
)
def get_game(game_id: int, session: SessionDep) -> GameOut:
    return GameOut.from_view(game_service.get_game(session, game_id))


@router.post(
    "/{game_id}/moves",
    status_code=status.HTTP_201_CREATED,
    response_model=GameOut,
    responses={**NOT_FOUND, **RULE_REFUSED, **INVALID},
    summary="Play a move for whoever's turn it is",
)
def play_move(game_id: int, move: MoveIn, session: SessionDep, response: Response) -> GameOut:
    view = game_service.play_move(session, game_id, board=move.board, cell=move.cell)
    # A move has no URL of its own; Location points at the game it changed (D29).
    response.headers["Location"] = _game_location(game_id)
    return GameOut.from_view(view)
