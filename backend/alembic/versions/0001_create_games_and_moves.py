"""Create games and moves.

Revision ID: 0001
Revises:
Create Date: 2026-10-01

Generated with `alembic revision --autogenerate`, then edited by hand: the
timestamp columns use plain sa.DateTime(timezone=True) instead of the app's
UTCDateTime wrapper, so this file never depends on application code.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "moves",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("board", sa.Integer(), nullable=False),
        sa.Column("cell", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("board BETWEEN 0 AND 8", name="ck_moves_board_range"),
        sa.CheckConstraint("cell BETWEEN 0 AND 8", name="ck_moves_cell_range"),
        sa.CheckConstraint("seq BETWEEN 0 AND 80", name="ck_moves_seq_range"),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "seq", name="uq_moves_game_id_seq"),
    )
    with op.batch_alter_table("moves") as batch_op:
        batch_op.create_index("ix_moves_game_id", ["game_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("moves") as batch_op:
        batch_op.drop_index("ix_moves_game_id")
    op.drop_table("moves")
    op.drop_table("games")
