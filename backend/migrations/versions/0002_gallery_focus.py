"""Add editable image focus to gallery items.

Revision ID: 0002_gallery_focus
Revises: 0001_initial
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_gallery_focus"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _columns() -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns("gallery_items")}


def upgrade() -> None:
    columns = _columns()
    if "focus_x" not in columns:
        op.add_column(
            "gallery_items",
            sa.Column("focus_x", sa.Float(), nullable=False, server_default="0.5"),
        )
    if "focus_y" not in columns:
        op.add_column(
            "gallery_items",
            sa.Column("focus_y", sa.Float(), nullable=False, server_default="0.5"),
        )


def downgrade() -> None:
    columns = _columns()
    if "focus_y" in columns:
        op.drop_column("gallery_items", "focus_y")
    if "focus_x" in columns:
        op.drop_column("gallery_items", "focus_x")
