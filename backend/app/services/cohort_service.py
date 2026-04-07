from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.errors import ApiError
from app.domain.models import (
    Cohort,
    CohortMembership,
    MembershipRole,
    ProgressCheckpoint,
    ProgressRecord,
    ProgressStatus,
    User,
)


class CohortService:
    def __init__(self, session) -> None:
        self._session = session

    async def list_progress_checkpoints(self, cohort_id: UUID) -> dict:
        cohort = await self._session.get(Cohort, cohort_id)
        if cohort is None:
            raise ApiError(404, "NOT_FOUND", "Cohort not found")

        stmt = (
            select(ProgressCheckpoint)
            .where(ProgressCheckpoint.cohort_id == cohort_id)
            .order_by(ProgressCheckpoint.sort_order, ProgressCheckpoint.id)
        )
        rows = (await self._session.scalars(stmt)).all()
        return {
            "items": [
                {
                    "id": r.id,
                    "code": r.code,
                    "title": r.title,
                    "sort_order": r.sort_order,
                    "required": r.required,
                }
                for r in rows
            ]
        }

    async def put_progress_record(
        self,
        *,
        cohort_id: UUID,
        membership_id: UUID,
        checkpoint_id: UUID,
        status: str,
        comment: Optional[str],
    ) -> dict:
        membership = await self._session.scalar(
            select(CohortMembership).where(
                CohortMembership.id == membership_id,
                CohortMembership.cohort_id == cohort_id,
            )
        )
        if membership is None:
            raise ApiError(404, "NOT_FOUND", "Membership not found")
        if membership.role != MembershipRole.student:
            raise ApiError(403, "FORBIDDEN", "Forbidden")

        checkpoint = await self._session.scalar(
            select(ProgressCheckpoint).where(
                ProgressCheckpoint.id == checkpoint_id,
                ProgressCheckpoint.cohort_id == cohort_id,
            )
        )
        if checkpoint is None:
            raise ApiError(404, "NOT_FOUND", "Checkpoint not found")

        st = ProgressStatus(status)
        record = await self._session.scalar(
            select(ProgressRecord).where(
                ProgressRecord.membership_id == membership_id,
                ProgressRecord.checkpoint_id == checkpoint_id,
            )
        )
        if record is None:
            record = ProgressRecord(
                membership_id=membership_id,
                checkpoint_id=checkpoint_id,
                status=st,
                comment=comment,
            )
            self._session.add(record)
        else:
            record.status = st
            record.comment = comment
        await self._session.flush()
        await self._session.refresh(record)

        updated_at = record.updated_at
        return {
            "id": record.id,
            "cohort_id": cohort_id,
            "membership_id": membership_id,
            "checkpoint_id": checkpoint_id,
            "status": record.status.value,
            "comment": record.comment,
            "updated_at": updated_at.isoformat().replace("+00:00", "Z"),
        }

    async def get_summary(self, cohort_id: UUID, viewer_membership_id: UUID) -> dict:
        cohort = await self._session.get(Cohort, cohort_id)
        if cohort is None:
            raise ApiError(404, "NOT_FOUND", "Cohort not found")

        viewer = await self._session.scalar(
            select(CohortMembership).where(
                CohortMembership.id == viewer_membership_id,
                CohortMembership.cohort_id == cohort_id,
            )
        )
        if viewer is None:
            raise ApiError(404, "NOT_FOUND", "Membership not found")
        if viewer.role != MembershipRole.teacher:
            raise ApiError(403, "FORBIDDEN", "Forbidden")

        checkpoints = (
            await self._session.scalars(
                select(ProgressCheckpoint)
                .where(ProgressCheckpoint.cohort_id == cohort_id)
                .order_by(ProgressCheckpoint.sort_order, ProgressCheckpoint.id)
            )
        ).all()

        memberships = (
            await self._session.scalars(
                select(CohortMembership)
                .options(selectinload(CohortMembership.user))
                .where(CohortMembership.cohort_id == cohort_id)
            )
        ).all()

        m_ids = [m.id for m in memberships]
        if not m_ids:
            records = []
        else:
            records = (
                await self._session.scalars(
                    select(ProgressRecord).where(ProgressRecord.membership_id.in_(m_ids))
                )
            ).all()
        rec_map: dict[tuple[UUID, UUID], ProgressStatus] = {}
        for r in records:
            rec_map[(r.membership_id, r.checkpoint_id)] = r.status

        participants = []
        for m in memberships:
            user: User = m.user
            progress: dict[str, str] = {}
            for cp in checkpoints:
                st = rec_map.get((m.id, cp.id), ProgressStatus.not_started)
                progress[str(cp.id)] = st.value
            participants.append(
                {
                    "membership_id": m.id,
                    "user_id": m.user_id,
                    "role": m.role.value,
                    "display_name": user.display_name,
                    "progress": progress,
                }
            )

        return {
            "cohort_id": cohort_id,
            "cohort_title": cohort.title,
            "checkpoints": [
                {
                    "id": cp.id,
                    "code": cp.code,
                    "title": cp.title,
                    "sort_order": cp.sort_order,
                    "required": cp.required,
                }
                for cp in checkpoints
            ],
            "participants": participants,
        }
