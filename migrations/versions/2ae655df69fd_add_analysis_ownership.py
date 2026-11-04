"""add analysis ownership

Revision ID: 2ae655df69fd
Revises: 4af4677804ff
Create Date: 2026-11-04 22:11:56.333729

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2ae655df69fd"
down_revision: str | Sequence[str] | None = "4af4677804ff"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "analyses",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )

    op.create_index(
        op.f("ix_analyses_user_id"),
        "analyses",
        ["user_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_analyses_user_id_users",
        "analyses",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_analyses_user_id_users",
        "analyses",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_analyses_user_id"),
        table_name="analyses",
    )

    op.drop_column("analyses", "user_id")
