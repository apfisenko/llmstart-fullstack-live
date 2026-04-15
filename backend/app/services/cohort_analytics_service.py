from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.errors import ApiError
from app.domain.models import (
    Cohort,
    CohortMembership,
    Dialogue,
    DialogueTurn,
    MembershipRole,
    MembershipStatus,
    ProgressCheckpoint,
    ProgressRecord,
    ProgressStatus,
    User,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _week_bounds(ref: datetime) -> tuple[datetime, datetime, datetime]:
    """Return (previous_week_start, current_week_start, next_week_start) in UTC."""
    ref = ref.astimezone(timezone.utc)
    weekday = ref.weekday()
    current_start = (ref - timedelta(days=weekday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    previous_start = current_start - timedelta(days=7)
    next_start = current_start + timedelta(days=7)
    return previous_start, current_start, next_start


def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


class CohortAnalyticsService:
    def __init__(self, session) -> None:
        self._session = session

    async def _require_teacher(self, cohort_id: UUID, viewer_membership_id: UUID) -> None:
        m = await self._session.scalar(
            select(CohortMembership).where(
                CohortMembership.id == viewer_membership_id,
                CohortMembership.cohort_id == cohort_id,
            )
        )
        if m is None:
            raise ApiError(404, "NOT_FOUND", "Membership not found")
        if m.role != MembershipRole.teacher:
            raise ApiError(403, "FORBIDDEN", "Forbidden")

    async def teacher_dashboard(
        self,
        *,
        cohort_id: UUID,
        viewer_membership_id: UUID,
        activity_days: int = 14,
        turns_limit: int = 20,
        q: Optional[str] = None,
        turns_cursor: Optional[str] = None,
    ) -> dict:
        activity_days = max(1, min(int(activity_days), 366))
        turns_limit = max(1, min(int(turns_limit), 100))
        await self._require_teacher(cohort_id, viewer_membership_id)

        cohort = await self._session.get(Cohort, cohort_id)
        if cohort is None:
            raise ApiError(404, "NOT_FOUND", "Cohort not found")

        prev_w, cur_w, next_w = _week_bounds(_utc_now())

        student_count = await self._session.scalar(
            select(func.count())
            .select_from(CohortMembership)
            .where(
                CohortMembership.cohort_id == cohort_id,
                CohortMembership.role == MembershipRole.student,
                CohortMembership.status == MembershipStatus.active,
            )
        )
        student_count = int(student_count or 0)

        async def _distinct_students_turns(start: datetime, end: datetime) -> int:
            q1 = (
                select(func.count(func.distinct(Dialogue.membership_id)))
                .select_from(DialogueTurn)
                .join(Dialogue, DialogueTurn.dialogue_id == Dialogue.id)
                .join(CohortMembership, Dialogue.membership_id == CohortMembership.id)
                .where(
                    CohortMembership.cohort_id == cohort_id,
                    CohortMembership.role == MembershipRole.student,
                    DialogueTurn.asked_at >= start,
                    DialogueTurn.asked_at < end,
                )
            )
            return int(await self._session.scalar(q1) or 0)

        active_prev = await _distinct_students_turns(prev_w, cur_w)
        active_cur = await _distinct_students_turns(cur_w, next_w)

        async def _homework_completed_events(start: datetime, end: datetime) -> int:
            q2 = (
                select(func.count())
                .select_from(ProgressRecord)
                .join(ProgressCheckpoint, ProgressRecord.checkpoint_id == ProgressCheckpoint.id)
                .join(CohortMembership, ProgressRecord.membership_id == CohortMembership.id)
                .where(
                    CohortMembership.cohort_id == cohort_id,
                    CohortMembership.role == MembershipRole.student,
                    ProgressCheckpoint.is_homework.is_(True),
                    ProgressRecord.status == ProgressStatus.completed,
                    ProgressRecord.updated_at >= start,
                    ProgressRecord.updated_at < end,
                )
            )
            return int(await self._session.scalar(q2) or 0)

        hw_prev = await _homework_completed_events(prev_w, cur_w)
        hw_cur = await _homework_completed_events(cur_w, next_w)

        async def _dialogue_questions(start: datetime, end: datetime) -> int:
            q3 = (
                select(func.count())
                .select_from(DialogueTurn)
                .join(Dialogue, DialogueTurn.dialogue_id == Dialogue.id)
                .join(CohortMembership, Dialogue.membership_id == CohortMembership.id)
                .where(
                    CohortMembership.cohort_id == cohort_id,
                    CohortMembership.role == MembershipRole.student,
                    DialogueTurn.asked_at >= start,
                    DialogueTurn.asked_at < end,
                )
            )
            return int(await self._session.scalar(q3) or 0)

        dq_prev = await _dialogue_questions(prev_w, cur_w)
        dq_cur = await _dialogue_questions(cur_w, next_w)

        checkpoints = await self._session.scalars(
            select(ProgressCheckpoint)
            .where(ProgressCheckpoint.cohort_id == cohort_id)
            .order_by(ProgressCheckpoint.sort_order, ProgressCheckpoint.id)
        )
        checkpoint_rows = list(checkpoints.all())
        total_cp = len(checkpoint_rows)

        stmt_ms = (
            select(CohortMembership)
            .options(selectinload(CohortMembership.user))
            .where(
                CohortMembership.cohort_id == cohort_id,
                CohortMembership.role == MembershipRole.student,
            )
        )
        student_memberships = list((await self._session.scalars(stmt_ms)).all())
        m_ids = [m.id for m in student_memberships]

        recs: list[ProgressRecord] = []
        if m_ids:
            recs = list(
                (
                    await self._session.scalars(
                        select(ProgressRecord).where(ProgressRecord.membership_id.in_(m_ids))
                    )
                ).all()
            )
        rec_map = {(r.membership_id, r.checkpoint_id): r for r in recs}

        avg_cur = 0.0
        avg_prev = 0.0
        if total_cp > 0 and student_memberships:
            scores = []
            for m in student_memberships:
                done = 0
                for cp in checkpoint_rows:
                    r = rec_map.get((m.id, cp.id))
                    if r and r.status == ProgressStatus.completed:
                        done += 1
                scores.append(done / total_cp * 100.0)
            avg_cur = sum(scores) / len(scores) if scores else 0.0
            avg_prev = avg_cur

        activity_by_day: list[dict] = []
        now = _utc_now()
        for i in range(activity_days - 1, -1, -1):
            day_start = (now - timedelta(days=i)).replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
            )
            day_end = day_start + timedelta(days=1)
            cnt = await self._session.scalar(
                select(func.count())
                .select_from(DialogueTurn)
                .join(Dialogue, DialogueTurn.dialogue_id == Dialogue.id)
                .join(CohortMembership, Dialogue.membership_id == CohortMembership.id)
                .where(
                    CohortMembership.cohort_id == cohort_id,
                    CohortMembership.role == MembershipRole.student,
                    DialogueTurn.asked_at >= day_start,
                    DialogueTurn.asked_at < day_end,
                )
            )
            activity_by_day.append(
                {"day": day_start.date().isoformat(), "question_count": int(cnt or 0)}
            )

        turn_stmt = (
            select(DialogueTurn, CohortMembership.id.label("m_id"), User.name)
            .join(Dialogue, DialogueTurn.dialogue_id == Dialogue.id)
            .join(CohortMembership, Dialogue.membership_id == CohortMembership.id)
            .join(User, CohortMembership.user_id == User.id)
            .where(
                CohortMembership.cohort_id == cohort_id,
                CohortMembership.role == MembershipRole.student,
            )
            .order_by(DialogueTurn.asked_at.desc())
            .limit(turns_limit + 1)
        )
        if q:
            turn_stmt = turn_stmt.where(DialogueTurn.question_text.ilike(f"%{q}%"))
        if turns_cursor:
            try:
                cursor_dt = datetime.fromisoformat(turns_cursor.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ApiError(422, "VALIDATION_ERROR", "Invalid turns_cursor") from exc
            turn_stmt = turn_stmt.where(DialogueTurn.asked_at < cursor_dt)

        turn_rows = list((await self._session.execute(turn_stmt)).all())
        next_cursor = None
        if len(turn_rows) > turns_limit:
            turn_rows = turn_rows[:turns_limit]
            if turn_rows:
                oldest = turn_rows[-1][0].asked_at
                next_cursor = _iso(oldest)
        turn_items = []
        for turn, mid, uname in turn_rows:
            t = turn
            turn_items.append(
                {
                    "membership_id": mid,
                    "user_message_id": t.id,
                    "assistant_message_id": t.assistant_message_id,
                    "student_display_name": uname,
                    "question_text": t.question_text,
                    "answer_text": t.answer_text,
                    "asked_at": _iso(t.asked_at),
                }
            )

        sub_stmt = (
            select(ProgressRecord, User.name, ProgressCheckpoint.title)
            .join(CohortMembership, ProgressRecord.membership_id == CohortMembership.id)
            .join(User, CohortMembership.user_id == User.id)
            .join(ProgressCheckpoint, ProgressRecord.checkpoint_id == ProgressCheckpoint.id)
            .where(
                CohortMembership.cohort_id == cohort_id,
                CohortMembership.role == MembershipRole.student,
                ProgressRecord.status == ProgressStatus.completed,
            )
            .order_by(ProgressRecord.updated_at.desc())
            .limit(30)
        )
        sub_rows = list((await self._session.execute(sub_stmt)).all())
        recent_submissions = []
        for pr, uname, ctitle in sub_rows:
            recent_submissions.append(
                {
                    "membership_id": pr.membership_id,
                    "student_display_name": uname,
                    "checkpoint_id": pr.checkpoint_id,
                    "checkpoint_title": ctitle,
                    "status": pr.status.value,
                    "comment": pr.comment,
                    "submission_links": pr.submission_links
                    if isinstance(pr.submission_links, list)
                    else None,
                    "updated_at": _iso(pr.updated_at),
                }
            )

        matrix: list[dict] = []
        for m in student_memberships:
            cells = []
            done = 0
            for cp in checkpoint_rows:
                r = rec_map.get((m.id, cp.id))
                st: ProgressStatus = r.status if r else ProgressStatus.not_started
                cells.append(
                    {
                        "checkpoint_id": cp.id,
                        "status": st.value,
                        "updated_at": _iso(r.updated_at) if r else None,
                    }
                )
                if r and r.status == ProgressStatus.completed:
                    done += 1
            matrix.append(
                {
                    "membership_id": m.id,
                    "display_name": m.user.name if m.user else None,
                    "score_completed": done,
                    "score_total": total_cp,
                    "cells": cells,
                }
            )
        matrix.sort(key=lambda row: row["score_completed"], reverse=True)

        return {
            "cohort_id": cohort_id,
            "cohort_title": cohort.title,
            "kpis": {
                "active_students": {"current_week": active_cur, "previous_week": active_prev},
                "homework_completed_events": {
                    "current_week": hw_cur,
                    "previous_week": hw_prev,
                },
                "avg_progress_percent": {
                    "current_week": round(avg_cur, 2),
                    "previous_week": round(avg_prev, 2),
                },
                "dialogue_questions": {"current_week": dq_cur, "previous_week": dq_prev},
            },
            "activity_by_day": activity_by_day,
            "recent_turns": {"items": turn_items, "next_cursor": next_cursor},
            "recent_submissions": recent_submissions,
            "matrix": matrix,
        }

    async def leaderboard(
        self,
        *,
        cohort_id: UUID,
        viewer_membership_id: Optional[UUID],
    ) -> dict:
        cohort = await self._session.get(Cohort, cohort_id)
        if cohort is None:
            raise ApiError(404, "NOT_FOUND", "Cohort not found")

        if viewer_membership_id is not None:
            m = await self._session.scalar(
                select(CohortMembership).where(
                    CohortMembership.id == viewer_membership_id,
                    CohortMembership.cohort_id == cohort_id,
                )
            )
            if m is None:
                raise ApiError(404, "NOT_FOUND", "Membership not found")

        checkpoint_rows = list(
            (
                await self._session.scalars(
                    select(ProgressCheckpoint)
                    .where(ProgressCheckpoint.cohort_id == cohort_id)
                    .order_by(ProgressCheckpoint.sort_order, ProgressCheckpoint.id)
                )
            ).all()
        )
        total_cp = len(checkpoint_rows)
        lesson_cp = sum(1 for c in checkpoint_rows if not c.is_homework)
        hw_cp = sum(1 for c in checkpoint_rows if c.is_homework)
        lesson_cp = max(lesson_cp, 1)
        hw_cp = max(hw_cp, 1)

        stmt_ms = (
            select(CohortMembership)
            .options(selectinload(CohortMembership.user))
            .where(
                CohortMembership.cohort_id == cohort_id,
                CohortMembership.role == MembershipRole.student,
            )
        )
        student_memberships = list((await self._session.scalars(stmt_ms)).all())
        m_ids = [m.id for m in student_memberships]
        recs: list[ProgressRecord] = []
        if m_ids:
            recs = list(
                (
                    await self._session.scalars(
                        select(ProgressRecord).where(ProgressRecord.membership_id.in_(m_ids))
                    )
                ).all()
            )
        rec_map = {(r.membership_id, r.checkpoint_id): r for r in recs}

        entries: list[dict] = []
        for m in student_memberships:
            per_cp: list[dict] = []
            completed = 0
            hw_done = 0
            lesson_done = 0
            for cp in checkpoint_rows:
                r = rec_map.get((m.id, cp.id))
                st = r.status if r else ProgressStatus.not_started
                per_cp.append({"checkpoint_id": cp.id, "status": st.value})
                if r and r.status == ProgressStatus.completed:
                    completed += 1
                    if cp.is_homework:
                        hw_done += 1
                    else:
                        lesson_done += 1
            pct = (completed / total_cp * 100.0) if total_cp else 0.0
            entries.append(
                {
                    "membership_id": m.id,
                    "user_id": m.user_id,
                    "display_name": m.user.name if m.user else None,
                    "progress_percent": round(pct, 2),
                    "completed_checkpoints": completed,
                    "total_checkpoints": total_cp,
                    "homework_completed": hw_done,
                    "lesson_completed": lesson_done,
                    "scatter_x": round(lesson_done / lesson_cp, 4),
                    "scatter_y": round(hw_done / hw_cp, 4),
                    "per_checkpoint": per_cp,
                    "_sort": completed,
                }
            )
        sorted_entries = sorted(entries, key=lambda e: (-e["_sort"], str(e["membership_id"])))
        entries_out = []
        for i, e in enumerate(sorted_entries, start=1):
            row = {k: v for k, v in e.items() if k != "_sort"}
            row["rank"] = i
            entries_out.append(row)

        checkpoints_out = [
            {
                "id": c.id,
                "code": c.code,
                "title": c.title,
                "sort_order": c.sort_order,
                "required": c.required,
                "is_homework": c.is_homework,
            }
            for c in checkpoint_rows
        ]

        return {
            "cohort_id": cohort_id,
            "checkpoints": checkpoints_out,
            "entries": entries_out,
        }

    async def student_progress_overview(
        self,
        *,
        cohort_id: UUID,
        membership_id: UUID,
    ) -> dict:
        m = await self._session.scalar(
            select(CohortMembership)
            .options(selectinload(CohortMembership.user))
            .where(
                CohortMembership.id == membership_id,
                CohortMembership.cohort_id == cohort_id,
            )
        )
        if m is None:
            raise ApiError(404, "NOT_FOUND", "Membership not found")
        if m.role != MembershipRole.student:
            raise ApiError(403, "FORBIDDEN", "Forbidden")

        checkpoint_rows = list(
            (
                await self._session.scalars(
                    select(ProgressCheckpoint)
                    .where(ProgressCheckpoint.cohort_id == cohort_id)
                    .order_by(ProgressCheckpoint.sort_order, ProgressCheckpoint.id)
                )
            ).all()
        )
        recs = list(
            (
                await self._session.scalars(
                    select(ProgressRecord).where(ProgressRecord.membership_id == membership_id)
                )
            ).all()
        )
        rec_by_cp = {r.checkpoint_id: r for r in recs}

        records_out = []
        for cp in checkpoint_rows:
            r = rec_by_cp.get(cp.id)
            records_out.append(
                {
                    "checkpoint_id": cp.id,
                    "status": (r.status.value if r else ProgressStatus.not_started.value),
                    "updated_at": _iso(r.updated_at) if r else None,
                    "comment": r.comment if r else None,
                    "submission_links": r.submission_links
                    if r and isinstance(r.submission_links, list)
                    else None,
                }
            )

        checkpoints_out = [
            {
                "id": c.id,
                "code": c.code,
                "title": c.title,
                "sort_order": c.sort_order,
                "required": c.required,
                "is_homework": c.is_homework,
            }
            for c in checkpoint_rows
        ]

        return {
            "cohort_id": cohort_id,
            "membership_id": membership_id,
            "display_name": m.user.name if m.user else None,
            "checkpoints": checkpoints_out,
            "records": records_out,
        }
