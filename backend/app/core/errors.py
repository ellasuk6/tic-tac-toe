"""Domain error types.

Services raise these. They know nothing about HTTP. In Stage 5 the API layer
gets one exception handler that turns any DomainError into the constitution's
error envelope: {"code": ..., "detail": ...}.
"""


class DomainError(Exception):
    """Base class. Every subclass sets a machine-readable `code`."""

    code: str = "domain_error"

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


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
