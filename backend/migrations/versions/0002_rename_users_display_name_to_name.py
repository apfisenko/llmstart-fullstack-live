"""rename users.display_name to name

Revision ID: 0002_user_name
Revises: 0001_initial
Create Date: 2026-04-08

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_user_name"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("users")}
    if "display_name" in cols and "name" not in cols:
        op.alter_column(
            "users",
            "display_name",
            new_column_name="name",
            existing_type=sa.String(length=255),
            existing_nullable=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("users")}
    if "name" in cols and "display_name" not in cols:
        op.alter_column(
            "users",
            "name",
            new_column_name="display_name",
            existing_type=sa.String(length=255),
            existing_nullable=True,
        )
