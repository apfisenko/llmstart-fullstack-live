"""seed demo cohort for frontend MVP (teacher @akozhin, students, progress, dialogues)

Revision ID: 0007_frontend_demo_seed
Revises: 0006_homework_flags
Create Date: 2026-04-15

Идемпотентно: если когорта с code = 'demo_frontend_mvp' уже есть — шаг пропускается.

Преподаватель: telegram_user_id 162684825, telegram_username akozhin (см. tasklist / plan задачи 02).
"""

from __future__ import annotations

import json
import uuid
from typing import Optional

import sqlalchemy as sa
from alembic import op

revision = "0007_frontend_demo_seed"
down_revision = "0006_homework_flags"
branch_labels = None
depends_on = None

DEMO_COHORT_CODE = "demo_frontend_mvp"

# Детерминированные UUID (удобно для ручных проверок и доков).
CID = uuid.UUID("f1eef000-0000-4000-8000-000000000001")
U_TEACHER = uuid.UUID("f1eef000-0000-4000-8000-000000000002")
U_S1 = uuid.UUID("f1eef000-0000-4000-8000-000000000003")
U_S2 = uuid.UUID("f1eef000-0000-4000-8000-000000000004")
U_S3 = uuid.UUID("f1eef000-0000-4000-8000-000000000005")
M_TEACHER = uuid.UUID("f1eef000-0000-4000-8000-000000000011")
M_S1 = uuid.UUID("f1eef000-0000-4000-8000-000000000012")
M_S2 = uuid.UUID("f1eef000-0000-4000-8000-000000000013")
M_S3 = uuid.UUID("f1eef000-0000-4000-8000-000000000014")
CP1 = uuid.UUID("f1eef000-0000-4000-8000-000000000021")
CP2 = uuid.UUID("f1eef000-0000-4000-8000-000000000022")
CP3 = uuid.UUID("f1eef000-0000-4000-8000-000000000023")
CP4 = uuid.UUID("f1eef000-0000-4000-8000-000000000024")
D_S1_WEB = uuid.UUID("f1eef000-0000-4000-8000-000000000031")
D_S2_TG = uuid.UUID("f1eef000-0000-4000-8000-000000000032")
TURN_A1 = uuid.UUID("f1eef000-0000-4000-8000-000000000051")
TURN_A2 = uuid.UUID("f1eef000-0000-4000-8000-000000000052")
TURN_B1 = uuid.UUID("f1eef000-0000-4000-8000-000000000053")
TURN_B2 = uuid.UUID("f1eef000-0000-4000-8000-000000000054")
TURN_C1 = uuid.UUID("f1eef000-0000-4000-8000-000000000055")
TURN_C2 = uuid.UUID("f1eef000-0000-4000-8000-000000000056")
TURN_D1 = uuid.UUID("f1eef000-0000-4000-8000-000000000057")
TURN_D2 = uuid.UUID("f1eef000-0000-4000-8000-000000000058")
TURN_E1 = uuid.UUID("f1eef000-0000-4000-8000-000000000059")
TURN_E2 = uuid.UUID("f1eef000-0000-4000-8000-00000000005a")


def upgrade() -> None:
    bind = op.get_bind()
    exists = bind.execute(
        sa.text("SELECT 1 FROM cohorts WHERE code = :code"),
        {"code": DEMO_COHORT_CODE},
    ).scalar_one_or_none()
    if exists is not None:
        return

    bind.execute(
        sa.text(
            """
            INSERT INTO cohorts (id, title, code, starts_at, ends_at, created_at, updated_at)
            VALUES (:id, :title, :code, NULL, NULL, NOW(), NOW())
            """
        ),
        {
            "id": CID,
            "title": "Demo cohort (frontend MVP)",
            "code": DEMO_COHORT_CODE,
        },
    )

    bind.execute(
        sa.text(
            """
            INSERT INTO users (id, telegram_user_id, telegram_username, name, created_at, updated_at)
            VALUES (:id, :tg_id, :tg_name, :name, NOW(), NOW())
            """
        ),
        {
            "id": U_TEACHER,
            "tg_id": "162684825",
            "tg_name": "akozhin",
            "name": "А. Кожин",
        },
    )
    for uid, uname, disp in [
        (U_S1, "demo_student_alpha", "Студент Альфа"),
        (U_S2, "demo_student_beta", "Студент Бета"),
        (U_S3, "demo_student_gamma", "Студент Гамма"),
    ]:
        bind.execute(
            sa.text(
                """
                INSERT INTO users (id, telegram_user_id, telegram_username, name, created_at, updated_at)
                VALUES (:id, NULL, :tg_name, :name, NOW(), NOW())
                """
            ),
            {"id": uid, "tg_name": uname, "name": disp},
        )

    bind.execute(
        sa.text(
            """
            INSERT INTO cohort_memberships (id, user_id, cohort_id, role, status, created_at, updated_at)
            VALUES (:id, :uid, :cid, 'teacher', 'active', NOW(), NOW())
            """
        ),
        {"id": M_TEACHER, "uid": U_TEACHER, "cid": CID},
    )
    bind.execute(
        sa.text(
            """
            INSERT INTO cohort_memberships (id, user_id, cohort_id, role, status, created_at, updated_at)
            VALUES (:id, :uid, :cid, 'student', 'active', NOW(), NOW())
            """
        ),
        {"id": M_S1, "uid": U_S1, "cid": CID},
    )
    bind.execute(
        sa.text(
            """
            INSERT INTO cohort_memberships (id, user_id, cohort_id, role, status, created_at, updated_at)
            VALUES (:id, :uid, :cid, 'student', 'active', NOW(), NOW())
            """
        ),
        {"id": M_S2, "uid": U_S2, "cid": CID},
    )
    bind.execute(
        sa.text(
            """
            INSERT INTO cohort_memberships (id, user_id, cohort_id, role, status, created_at, updated_at)
            VALUES (:id, :uid, :cid, 'student', 'active', NOW(), NOW())
            """
        ),
        {"id": M_S3, "uid": U_S3, "cid": CID},
    )

    for cp_id, code, title, sort_order, required, is_hw in [
        (CP1, "lesson_01", "Урок 1 — вводная", 1, True, False),
        (CP2, "lesson_02", "Урок 2 — практика", 2, True, False),
        (CP3, "hw_01", "Домашка 1", 3, True, True),
        (CP4, "hw_02", "Домашка 2", 4, False, True),
    ]:
        bind.execute(
            sa.text(
                """
                INSERT INTO progress_checkpoints (
                    id, cohort_id, code, title, sort_order, required, is_homework
                )
                VALUES (:id, :cid, :code, :title, :so, :req, :hw)
                """
            ),
            {
                "id": cp_id,
                "cid": CID,
                "code": code,
                "title": title,
                "so": sort_order,
                "req": required,
                "hw": is_hw,
            },
        )

    def ins_record(
        mid: uuid.UUID,
        cpid: uuid.UUID,
        status: str,
        comment: Optional[str],
        links: Optional[list],
    ):
        rec_id = uuid.uuid5(CID, f"progress:{mid}:{cpid}")
        bind.execute(
            sa.text(
                """
                INSERT INTO progress_records (
                    id, membership_id, checkpoint_id, status, comment, submission_links, updated_at
                )
                VALUES (
                    :id, :mid, :cpid, :status, :comment,
                    CAST(:links AS jsonb),
                    NOW()
                )
                """
            ),
            {
                "id": rec_id,
                "mid": mid,
                "cpid": cpid,
                "status": status,
                "comment": comment,
                "links": json.dumps(links) if links is not None else None,
            },
        )

    # Студент 1: два урока completed, одна ДЗ in_progress
    ins_record(M_S1, CP1, "completed", "Готово", None)
    ins_record(M_S1, CP2, "completed", None, None)
    ins_record(M_S1, CP3, "in_progress", "Делаю", None)
    # Студент 2: всё completed, у ДЗ ссылки
    ins_record(M_S2, CP1, "completed", None, None)
    ins_record(M_S2, CP2, "completed", None, None)
    ins_record(M_S2, CP3, "completed", "Сдано", ["https://example.com/demo-hw1"])
    ins_record(M_S2, CP4, "completed", None, ["https://example.com/demo-hw2"])
    # Студент 3: минимальный прогресс
    ins_record(M_S3, CP1, "completed", None, None)

    bind.execute(
        sa.text(
            """
            INSERT INTO dialogues (id, membership_id, channel, state, updated_at)
            VALUES (:id, :mid, 'web', 'active', NOW())
            """
        ),
        {"id": D_S1_WEB, "mid": M_S1},
    )
    bind.execute(
        sa.text(
            """
            INSERT INTO dialogues (id, membership_id, channel, state, updated_at)
            VALUES (:id, :mid, 'telegram', 'active', NOW())
            """
        ),
        {"id": D_S2_TG, "mid": M_S2},
    )

    def ins_turn(
        umid: uuid.UUID,
        amid: uuid.UUID,
        did: uuid.UUID,
        q: str,
        a: str,
        days_ago: float,
    ) -> None:
        bind.execute(
            sa.text(
                """
                INSERT INTO dialogue_turns (
                    id, assistant_message_id, dialogue_id,
                    question_text, answer_text, asked_at, answered_at
                )
                VALUES (
                    :umid, :amid, :did, :q, :a,
                    NOW() - (interval '1 day' * CAST(:days AS double precision)) - interval '1 hour',
                    NOW() - (interval '1 day' * CAST(:days AS double precision)) - interval '59 minutes'
                )
                """
            ),
            {"umid": umid, "amid": amid, "did": did, "q": q, "a": a, "days": days_ago},
        )

    ins_turn(TURN_A1, TURN_A2, D_S1_WEB, "Что такое FastAPI?", "FastAPI — ASGI-фреймворк для Python.", 1.5)
    ins_turn(
        TURN_B1,
        TURN_B2,
        D_S1_WEB,
        "Как подключить PostgreSQL?",
        "Используйте asyncpg и SQLAlchemy 2 с async engine.",
        3.0,
    )
    ins_turn(
        TURN_C1,
        TURN_C2,
        D_S1_WEB,
        "Нужен пример пагинации курсором.",
        "Сохраняйте next_before_asked_at и передавайте before_asked_at.",
        5.0,
    )
    ins_turn(TURN_D1, TURN_D2, D_S2_TG, "Привет из Telegram", "Привет! Чем помочь?", 2.0)
    ins_turn(
        TURN_E1,
        TURN_E2,
        D_S2_TG,
        "Как сдать домашку?",
        "Через PUT progress-records с submission_links.",
        4.0,
    )


def downgrade() -> None:
    bind = op.get_bind()
    row = bind.execute(
        sa.text("SELECT id FROM cohorts WHERE code = :code"),
        {"code": DEMO_COHORT_CODE},
    ).fetchone()
    if row is None:
        return
    cohort_id = row[0]

    bind.execute(
        sa.text(
            """
            DELETE FROM dialogue_turns
            WHERE dialogue_id IN (SELECT id FROM dialogues WHERE membership_id IN (
                SELECT id FROM cohort_memberships WHERE cohort_id = :cid
            ))
            """
        ),
        {"cid": cohort_id},
    )
    bind.execute(
        sa.text(
            """
            DELETE FROM dialogues WHERE membership_id IN (
                SELECT id FROM cohort_memberships WHERE cohort_id = :cid
            )
            """
        ),
        {"cid": cohort_id},
    )
    bind.execute(
        sa.text(
            """
            DELETE FROM progress_records WHERE membership_id IN (
                SELECT id FROM cohort_memberships WHERE cohort_id = :cid
            )
            """
        ),
        {"cid": cohort_id},
    )
    bind.execute(sa.text("DELETE FROM progress_checkpoints WHERE cohort_id = :cid"), {"cid": cohort_id})
    bind.execute(sa.text("DELETE FROM cohort_memberships WHERE cohort_id = :cid"), {"cid": cohort_id})
    bind.execute(sa.text("DELETE FROM cohorts WHERE id = :cid"), {"cid": cohort_id})

    for uid in (U_TEACHER, U_S1, U_S2, U_S3):
        bind.execute(sa.text("DELETE FROM users WHERE id = :id"), {"id": uid})
