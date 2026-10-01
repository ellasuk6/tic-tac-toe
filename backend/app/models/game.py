"""Tables: games and moves.

Only facts that cannot be worked out from anything else are stored (DECISIONS.md, D4):
a game exists, and its moves happened in a given order. Board contents, who is
winning, whose turn it is, and which board is next are all computed by
app/services/rules.py from the moves.
"""

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, UTCDateTime, utc_now


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)

    moves: Mapped[list["Move"]] = relationship(  # quoted: Move is defined below
        back_populates="game", order_by="Move.seq", cascade="all, delete-orphan"
    )


class Move(Base):
    __tablename__ = "moves"
    __table_args__ = (
        # A game cannot have two "move number 5"s.
        UniqueConstraint("game_id", "seq", name="uq_moves_game_id_seq"),
        CheckConstraint("seq BETWEEN 0 AND 80", name="ck_moves_seq_range"),
        CheckConstraint("board BETWEEN 0 AND 8", name="ck_moves_board_range"),
        CheckConstraint("cell BETWEEN 0 AND 8", name="ck_moves_cell_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), index=True)
    # Order within the game, starting at 0. Even seq = X's move, odd = O's: the player
    # is derived from seq, so it is not stored (D20).
    seq: Mapped[int]
    board: Mapped[int]
    cell: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)

    game: Mapped[Game] = relationship(back_populates="moves")
