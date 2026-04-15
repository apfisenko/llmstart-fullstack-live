from __future__ import annotations

from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from app.api.errors import ApiError
from app.domain.models import MembershipRole, ProgressRecord, ProgressStatus, User
from app.infrastructure.repositories.cohort_progress_repository import CohortProgressRepository


class CohortService:
    def __init__(self, session) -> None:
        self._session = session
        self._progress = CohortProgressRepository(session)

    async def list_progress_checkpoints(self, cohort_id: UUID) -> dict:
        cohort = await self._progress.get_cohort(cohort_id)
        if cohort is None:
            raise ApiError(404, "NOT_FOUND", "Cohort not found")

        rows = await self._progress.checkpoints_ordered(cohort_id)
        return {
            "items": [
                {
                    "id": r.id,
                    "code": r.code,
                    "title": r.title,
                    "sort_order": r.sort_order,
                    "required": r.required,
                    "is_homework": r.is_homework,
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
        submission_links: Optional[Sequence[str]] = None,
    ) -> dict:
        membership = await self._progress.membership_in_cohort(cohort_id, membership_id)
        if membership is None:
            raise ApiError(404, "NOT_FOUND", "Membership not found")
        if membership.role != MembershipRole.student:
            raise ApiError(403, "FORBIDDEN", "Forbidden")

        checkpoint = await self._progress.checkpoint_in_cohort(cohort_id, checkpoint_id)
        if checkpoint is None:
            raise ApiError(404, "NOT_FOUND", "Checkpoint not found")

        st = ProgressStatus(status)
        links: Optional[list[str]] = None
        if submission_links is not None:
            if len(list(submission_links)) > 32:
                raise ApiError(422, "VALIDATION_ERROR", "Too many submission_links")
            links = list(submission_links)

        record = await self._progress.progress_record(membership_id, checkpoint_id)
        if record is None:
            record = ProgressRecord(
                membership_id=membership_id,
                checkpoint_id=checkpoint_id,
                status=st,
                comment=comment,
                submission_links=links,
            )
            self._progress.add_progress_record(record)
        else:
            record.status = st
            record.comment = comment
            if links is not None:
                record.submission_links = links
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
            "submission_links": record.submission_links
            if isinstance(record.submission_links, list)
            else None,
            "updated_at": updated_at.isoformat().replace("+00:00", "Z"),
        }

    async def get_summary(self, cohort_id: UUID, viewer_membership_id: UUID) -> dict:
        cohort = await self._progress.get_cohort(cohort_id)
        if cohort is None:
            raise ApiError(404, "NOT_FOUND", "Cohort not found")

        viewer = await self._progress.membership_in_cohort(cohort_id, viewer_membership_id)
        if viewer is None:
            raise ApiError(404, "NOT_FOUND", "Membership not found")
        if viewer.role != MembershipRole.teacher:
            raise ApiError(403, "FORBIDDEN", "Forbidden")

        checkpoints = await self._progress.checkpoints_ordered(cohort_id)
        memberships = await self._progress.memberships_with_users(cohort_id)

        m_ids = [m.id for m in memberships]
        records = await self._progress.progress_records_for_memberships(m_ids)
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
                    "name": user.name,
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
                    "is_homework": cp.is_homework,
                }
                for cp in checkpoints
            ],
            "participants": participants,
        }
