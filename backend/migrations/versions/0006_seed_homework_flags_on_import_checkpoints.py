"""mark homework checkpoints from progress-import seed (code hw_*)

Revision ID: 0006_homework_flags
Revises: 0005_frontend_fields
Create Date: 2026-04-15

Идемпотентно: обновляет только строки с code LIKE 'hw_%'.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0006_homework_flags"
down_revision = "0005_frontend_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            UPDATE progress_checkpoints
            SET is_homework = TRUE
            WHERE code LIKE 'hw_%'
            """
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            UPDATE progress_checkpoints
            SET is_homework = FALSE
            WHERE code LIKE 'hw_%'
            """
        )
    )
