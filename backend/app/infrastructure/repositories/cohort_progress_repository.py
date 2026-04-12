from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models import (
    Cohort,
    CohortMembership,
    ProgressCheckpoint,
    ProgressRecord,
)


class CohortProgressRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_cohort(self, cohort_id: UUID) -> Cohort | None:
        return await self._session.get(Cohort, cohort_id)

    async def checkpoints_ordered(self, cohort_id: UUID) -> list[ProgressCheckpoint]:
        stmt = (
            select(ProgressCheckpoint)
            .where(ProgressCheckpoint.cohort_id == cohort_id)
            .order_by(ProgressCheckpoint.sort_order, ProgressCheckpoint.id)
        )
        return list((await self._session.scalars(stmt)).all())

    async def membership_in_cohort(
        self, cohort_id: UUID, membership_id: UUID
    ) -> CohortMembership | None:
        return await self._session.scalar(
            select(CohortMembership).where(
                CohortMembership.id == membership_id,
                CohortMembership.cohort_id == cohort_id,
            )
        )

    async def checkpoint_in_cohort(
        self, cohort_id: UUID, checkpoint_id: UUID
    ) -> ProgressCheckpoint | None:
        return await self._session.scalar(
            select(ProgressCheckpoint).where(
                ProgressCheckpoint.id == checkpoint_id,
                ProgressCheckpoint.cohort_id == cohort_id,
            )
        )

    async def progress_record(
        self, membership_id: UUID, checkpoint_id: UUID
    ) -> ProgressRecord | None:
        return await self._session.scalar(
            select(ProgressRecord).where(
                ProgressRecord.membership_id == membership_id,
                ProgressRecord.checkpoint_id == checkpoint_id,
            )
        )

    def add_progress_record(self, record: ProgressRecord) -> None:
        self._session.add(record)

    async def memberships_with_users(self, cohort_id: UUID) -> list[CohortMembership]:
        stmt = (
            select(CohortMembership)
            .options(selectinload(CohortMembership.user))
            .where(CohortMembership.cohort_id == cohort_id)
        )
        return list((await self._session.scalars(stmt)).all())

    async def progress_records_for_memberships(
        self, membership_ids: list[UUID]
    ) -> list[ProgressRecord]:
        if not membership_ids:
            return []
        stmt = select(ProgressRecord).where(ProgressRecord.membership_id.in_(membership_ids))
        return list((await self._session.scalars(stmt)).all())
