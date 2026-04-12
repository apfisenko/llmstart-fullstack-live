"""dialogue_messages -> dialogue_turns

Revision ID: 0004_dialogue_turns
Revises: 0003_seed_progress
Create Date: 2026-04-12

"""

from __future__ import annotations

from collections import defaultdict

import sqlalchemy as sa
from alembic import op

revision = "0004_dialogue_turns"
down_revision = "0003_seed_progress"
branch_labels = None
depends_on = None


def _role_value(role: object) -> str:
    if isinstance(role, str):
        return role
    return getattr(role, "value", str(role))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()
    has_turns = "dialogue_turns" in tables
    has_messages = "dialogue_messages" in tables

    # Свежий `db-reset`: 0001 делает create_all по текущим моделям — уже есть dialogue_turns.
    if not has_turns:
        op.create_table(
            "dialogue_turns",
            sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("assistant_message_id", sa.Uuid(as_uuid=True), nullable=False),
            sa.Column("dialogue_id", sa.Uuid(as_uuid=True), nullable=False),
            sa.Column("question_text", sa.Text(), nullable=False),
            sa.Column("answer_text", sa.Text(), nullable=False),
            sa.Column("asked_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(
                ["dialogue_id"],
                ["dialogues.id"],
                ondelete="CASCADE",
            ),
            sa.UniqueConstraint(
                "assistant_message_id",
                name="uq_dialogue_turns_assistant_message_id",
            ),
            sa.CheckConstraint(
                "answered_at >= asked_at",
                name="ck_dialogue_turns_answer_after_question",
            ),
        )
        op.create_index(
            "ix_dialogue_turns_dialogue_asked",
            "dialogue_turns",
            ["dialogue_id", "asked_at"],
            unique=False,
        )

    if not has_messages:
        return

    rows = bind.execute(
        sa.text(
            "SELECT id, dialogue_id, role, content, created_at "
            "FROM dialogue_messages ORDER BY dialogue_id, created_at"
        )
    ).fetchall()

    by_dialogue: dict[object, list] = defaultdict(list)
    for row in rows:
        by_dialogue[row.dialogue_id].append(row)

    insert = sa.text(
        """
        INSERT INTO dialogue_turns (
            id, assistant_message_id, dialogue_id,
            question_text, answer_text, asked_at, answered_at
        )
        VALUES (
            :id, :assistant_message_id, :dialogue_id,
            :question_text, :answer_text, :asked_at, :answered_at
        )
        """
    )

    for _did, msgs in by_dialogue.items():
        i = 0
        while i < len(msgs):
            row = msgs[i]
            if _role_value(row.role) == "system":
                i += 1
                continue
            if _role_value(row.role) != "user":
                i += 1
                continue
            user_row = row
            i += 1
            if i >= len(msgs):
                break
            nxt = msgs[i]
            if _role_value(nxt.role) != "assistant":
                continue
            assistant_row = nxt
            i += 1
            bind.execute(
                insert,
                {
                    "id": user_row.id,
                    "assistant_message_id": assistant_row.id,
                    "dialogue_id": user_row.dialogue_id,
                    "question_text": user_row.content,
                    "answer_text": assistant_row.content,
                    "asked_at": user_row.created_at,
                    "answered_at": assistant_row.created_at,
                },
            )

    op.drop_table("dialogue_messages")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "dialogue_messages" not in inspector.get_table_names():
        op.create_table(
            "dialogue_messages",
            sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("dialogue_id", sa.Uuid(as_uuid=True), nullable=False),
            sa.Column("role", sa.String(length=50), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(
                ["dialogue_id"],
                ["dialogues.id"],
                ondelete="CASCADE",
            ),
        )

    inspector = sa.inspect(bind)
    if "dialogue_turns" not in inspector.get_table_names():
        return

    turns = bind.execute(
        sa.text(
            "SELECT id, assistant_message_id, dialogue_id, question_text, answer_text, "
            "asked_at, answered_at FROM dialogue_turns ORDER BY dialogue_id, asked_at"
        )
    ).fetchall()

    ins_user = sa.text(
        """
        INSERT INTO dialogue_messages (id, dialogue_id, role, content, created_at)
        VALUES (:id, :dialogue_id, :role, :content, :created_at)
        """
    )
    ins_asst = sa.text(
        """
        INSERT INTO dialogue_messages (id, dialogue_id, role, content, created_at)
        VALUES (:id, :dialogue_id, :role, :content, :created_at)
        """
    )

    for t in turns:
        bind.execute(
            ins_user,
            {
                "id": t.id,
                "dialogue_id": t.dialogue_id,
                "role": "user",
                "content": t.question_text,
                "created_at": t.asked_at,
            },
        )
        bind.execute(
            ins_asst,
            {
                "id": t.assistant_message_id,
                "dialogue_id": t.dialogue_id,
                "role": "assistant",
                "content": t.answer_text,
                "created_at": t.answered_at,
            },
        )

    op.drop_index("ix_dialogue_turns_dialogue_asked", table_name="dialogue_turns")
    op.drop_table("dialogue_turns")
