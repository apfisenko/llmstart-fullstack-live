"""frontend fields: telegram_username, is_homework, submission_links

Revision ID: 0005_frontend_fields
Revises: 6480de72d688
Create Date: 2026-04-15

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005_frontend_fields"
down_revision = "6480de72d688"
branch_labels = None
depends_on = None


def _table_columns(insp: sa.Inspection, table: str) -> set[str]:
    return {c["name"] for c in insp.get_columns(table)}


def _index_exists(bind: sa.Connection, name: str) -> bool:
    row = bind.execute(
        sa.text("SELECT 1 FROM pg_indexes WHERE indexname = :n LIMIT 1"),
        {"n": name},
    ).scalar_one_or_none()
    return row is not None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # 0001_initial использует create_all() по текущим моделям — часть колонок уже может быть в БД.
    if "telegram_username" not in _table_columns(insp, "users"):
        op.add_column("users", sa.Column("telegram_username", sa.String(255), nullable=True))

    if not _index_exists(bind, "uq_users_telegram_username_lower"):
        op.execute(
            """
            CREATE UNIQUE INDEX uq_users_telegram_username_lower
            ON users (lower(telegram_username))
            WHERE telegram_username IS NOT NULL
            """
        )

    if "is_homework" not in _table_columns(insp, "progress_checkpoints"):
        op.add_column(
            "progress_checkpoints",
            sa.Column("is_homework", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )
        op.alter_column("progress_checkpoints", "is_homework", server_default=None)

    if "submission_links" not in _table_columns(insp, "progress_records"):
        op.add_column(
            "progress_records",
            sa.Column("submission_links", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("progress_records", "submission_links", if_exists=True)
    op.drop_column("progress_checkpoints", "is_homework", if_exists=True)
    op.execute("DROP INDEX IF EXISTS uq_users_telegram_username_lower")
    op.drop_column("users", "telegram_username", if_exists=True)
