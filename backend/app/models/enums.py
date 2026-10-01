"""Domain enums.

StrEnum values are plain lowercase strings, so they appear in the API exactly as
written here (the constitution requires lowercase snake_case enum values).

This file imports nothing from SQLAlchemy, so the pure rules engine can use it.
"""

from enum import StrEnum


class Player(StrEnum):
    X = "x"
    O = "o"  # noqa: E741  (the player is literally named O)

    @property
    def opponent(self) -> "Player":  # quoted: the class is still being defined here
        return Player.O if self is Player.X else Player.X


class BoardStatus(StrEnum):
    """Status of one small board."""

    OPEN = "open"
    X_WON = "x_won"
    O_WON = "o_won"
    DRAW = "draw"  # full, nobody has three in a row


class GameStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    X_WON = "x_won"
    O_WON = "o_won"
    DRAW = "draw"
