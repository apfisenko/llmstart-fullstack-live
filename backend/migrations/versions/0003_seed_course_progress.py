"""seed course progress from data/progress-import.v1.json

Revision ID: 0003_seed_progress
Revises: 0002_user_name
Create Date: 2026-04-12

Сид рассчитан на пустую БД после `make db-reset`. Повторный upgrade безопасен: если когорта
с тем же title уже есть — шаг пропускается.

Время submitted_at без суффикса таймзоны интерпретируется как Europe/Moscow (см. meta JSON).
progress_status \"done\" из импорта маппится в значение ORM/API `completed`.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import sqlalchemy as sa
from alembic import op

revision = "0003_seed_progress"
down_revision = "0002_user_name"
branch_labels = None
depends_on = None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_payload() -> dict:
    path = _repo_root() / "data" / "progress-import.v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_submitted_at(raw: str) -> datetime:
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("Europe/Moscow"))
    return dt


def upgrade() -> None:
    payload = _load_payload()
    cohort_title = str(payload["flow_hint"]["title"])
    bind = op.get_bind()

    exists = bind.execute(
        sa.text("SELECT id FROM cohorts WHERE title = :title"),
        {"title": cohort_title},
    ).scalar_one_or_none()
    if exists is not None:
        return

    cohort_id = uuid.uuid4()
    bind.execute(
        sa.text(
            """
            INSERT INTO cohorts (id, title, code, starts_at, ends_at, created_at, updated_at)
            VALUES (:id, :title, NULL, NULL, NULL, NOW(), NOW())
            """
        ),
        {"id": cohort_id, "title": cohort_title},
    )

    telegram_to_user_id: dict[int, uuid.UUID] = {}
    for row in payload["students"]:
        tid = int(row["telegram_id"])
        uid = uuid.uuid4()
        telegram_to_user_id[tid] = uid
        bind.execute(
            sa.text(
                """
                INSERT INTO users (id, telegram_user_id, name, created_at, updated_at)
                VALUES (:id, :tg, :name, NOW(), NOW())
                """
            ),
            {"id": uid, "tg": str(tid), "name": row.get("name")},
        )

    telegram_to_membership_id: dict[int, uuid.UUID] = {}
    for tid, uid in telegram_to_user_id.items():
        mid = uuid.uuid4()
        telegram_to_membership_id[tid] = mid
        bind.execute(
            sa.text(
                """
                INSERT INTO cohort_memberships (
                    id, user_id, cohort_id, role, status, created_at, updated_at
                )
                VALUES (
                    :id, :user_id, :cohort_id, 'student', 'active', NOW(), NOW()
                )
                """
            ),
            {"id": mid, "user_id": uid, "cohort_id": cohort_id},
        )

    lesson_positions = sorted({int(s["lesson_position"]) for s in payload["submissions"]})
    lesson_to_checkpoint_id: dict[int, uuid.UUID] = {}
    for pos in lesson_positions:
        cp_id = uuid.uuid4()
        lesson_to_checkpoint_id[pos] = cp_id
        code = f"hw_{pos}"
        title = f"Домашка {pos}"
        bind.execute(
            sa.text(
                """
                INSERT INTO progress_checkpoints (
                    id, cohort_id, code, title, sort_order, required
                )
                VALUES (:id, :cohort_id, :code, :title, :sort_order, TRUE)
                """
            ),
            {
                "id": cp_id,
                "cohort_id": cohort_id,
                "code": code,
                "title": title,
                "sort_order": pos,
            },
        )

    for sub in payload["submissions"]:
        tid = int(sub["student_telegram_id"])
        pos = int(sub["lesson_position"])
        raw_status = str(sub.get("progress_status", "done"))
        if raw_status != "done":
            raise RuntimeError(f"Unexpected progress_status in import: {raw_status!r}")
        membership_id = telegram_to_membership_id[tid]
        checkpoint_id = lesson_to_checkpoint_id[pos]
        rid = uuid.uuid4()
        comment = sub.get("summary_text") or ""
        updated_at = _parse_submitted_at(str(sub["submitted_at"]))
        bind.execute(
            sa.text(
                """
                INSERT INTO progress_records (
                    id, membership_id, checkpoint_id, status, comment, updated_at
                )
                VALUES (
                    :id, :membership_id, :checkpoint_id, 'completed', :comment, :updated_at
                )
                """
            ),
            {
                "id": rid,
                "membership_id": membership_id,
                "checkpoint_id": checkpoint_id,
                "comment": comment,
                "updated_at": updated_at,
            },
        )


def downgrade() -> None:
    payload = _load_payload()
    cohort_title = str(payload["flow_hint"]["title"])
    student_telegram_ids = [str(int(s["telegram_id"])) for s in payload["students"]]
    bind = op.get_bind()

    row = bind.execute(
        sa.text("SELECT id FROM cohorts WHERE title = :title"),
        {"title": cohort_title},
    ).fetchone()
    if row is None:
        return
    cohort_id = row[0]

    bind.execute(
        sa.text(
            """
            DELETE FROM progress_records
            WHERE membership_id IN (
                SELECT id FROM cohort_memberships WHERE cohort_id = :cid
            )
            """
        ),
        {"cid": cohort_id},
    )
    bind.execute(
        sa.text("DELETE FROM progress_checkpoints WHERE cohort_id = :cid"),
        {"cid": cohort_id},
    )
    bind.execute(
        sa.text("DELETE FROM cohort_memberships WHERE cohort_id = :cid"),
        {"cid": cohort_id},
    )
    bind.execute(
        sa.text("DELETE FROM cohorts WHERE id = :cid"),
        {"cid": cohort_id},
    )

    for tg in student_telegram_ids:
        bind.execute(
            sa.text("DELETE FROM users WHERE telegram_user_id = :tg"),
            {"tg": tg},
        )
