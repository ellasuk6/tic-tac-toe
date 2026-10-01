"""Domain error types.

Services raise these. They know nothing about HTTP. The API layer
(app/api/v1/errors.py) turns each kind into a status code and the constitution's
error envelope: {"code": ..., "detail": ...}.
"""


class DomainError(Exception):
    """Base class. Every subclass sets a machine-readable `code`."""

    code: str = "domain_error"

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class NotFoundError(DomainError):
    """The requested thing does not exist (the API will answer 404)."""


class GameNotFoundError(NotFoundError):
    code = "game_not_found"


class RuleViolationError(DomainError):
    """A game rule refused the move (the API will answer 409)."""


class GameOverError(RuleViolationError):
    code = "game_over"


class BoardNotPlayableError(RuleViolationError):
    """The player was sent to a different board."""

    code = "board_not_playable"


class BoardDecidedError(RuleViolationError):
    """The chosen board is already won or full."""

    code = "board_decided"


class CellOccupiedError(RuleViolationError):
    code = "cell_occupied"


class MoveConflictError(RuleViolationError):
    """Another move was saved for this game at the same moment (e.g. a double click)."""

    code = "move_conflict"
