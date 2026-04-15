from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    CohortAnalyticsServiceDep,
    CohortServiceDep,
    require_client_token_if_configured,
)
from app.api.v1.schemas_frontend import (
    LeaderboardResponse,
    StudentProgressOverviewResponse,
    TeacherDashboardResponse,
)
from app.api.v1.schemas_progress import (
    CohortSummaryResponse,
    ProgressCheckpointListResponse,
    ProgressRecordResponse,
    PutProgressRecordRequest,
)

router = APIRouter(dependencies=[Depends(require_client_token_if_configured)])


@router.get(
    "/cohorts/{cohort_id}/progress-checkpoints",
    response_model=ProgressCheckpointListResponse,
)
async def list_progress_checkpoints(
    cohort_id: UUID,
    service: CohortServiceDep,
) -> ProgressCheckpointListResponse:
    data = await service.list_progress_checkpoints(cohort_id)
    return ProgressCheckpointListResponse.model_validate(data)


@router.put(
    "/cohorts/{cohort_id}/memberships/{membership_id}/progress-records/{checkpoint_id}",
    response_model=ProgressRecordResponse,
)
async def put_progress_record(
    cohort_id: UUID,
    membership_id: UUID,
    checkpoint_id: UUID,
    body: PutProgressRecordRequest,
    service: CohortServiceDep,
) -> ProgressRecordResponse:
    data = await service.put_progress_record(
        cohort_id=cohort_id,
        membership_id=membership_id,
        checkpoint_id=checkpoint_id,
        status=body.status.value,
        comment=body.comment,
        submission_links=body.submission_links,
    )
    return ProgressRecordResponse.model_validate(data)


@router.get(
    "/cohorts/{cohort_id}/summary",
    response_model=CohortSummaryResponse,
)
async def get_cohort_summary(
    cohort_id: UUID,
    service: CohortServiceDep,
    viewer_membership_id: UUID = Query(
        ...,
        description=("Идентификатор участия преподавателя в потоке (MVP при общем Bearer)."),
    ),
) -> CohortSummaryResponse:
    data = await service.get_summary(cohort_id, viewer_membership_id)
    return CohortSummaryResponse.model_validate(data)


@router.get(
    "/cohorts/{cohort_id}/teacher-dashboard",
    response_model=TeacherDashboardResponse,
)
async def get_cohort_teacher_dashboard(
    cohort_id: UUID,
    service: CohortAnalyticsServiceDep,
    viewer_membership_id: UUID = Query(
        ...,
        description="Идентификатор участия преподавателя в потоке (MVP при общем Bearer).",
    ),
    activity_days: int = Query(14, ge=1, le=366),
    turns_cursor: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None),
) -> TeacherDashboardResponse:
    data = await service.teacher_dashboard(
        cohort_id=cohort_id,
        viewer_membership_id=viewer_membership_id,
        activity_days=activity_days,
        turns_limit=limit,
        q=q,
        turns_cursor=turns_cursor,
    )
    return TeacherDashboardResponse.model_validate(data)


@router.get(
    "/cohorts/{cohort_id}/leaderboard",
    response_model=LeaderboardResponse,
)
async def get_cohort_leaderboard(
    cohort_id: UUID,
    service: CohortAnalyticsServiceDep,
    viewer_membership_id: Optional[UUID] = Query(None),
) -> LeaderboardResponse:
    data = await service.leaderboard(
        cohort_id=cohort_id,
        viewer_membership_id=viewer_membership_id,
    )
    return LeaderboardResponse.model_validate(data)


@router.get(
    "/cohorts/{cohort_id}/memberships/{membership_id}/progress-overview",
    response_model=StudentProgressOverviewResponse,
)
async def get_membership_progress_overview(
    cohort_id: UUID,
    membership_id: UUID,
    service: CohortAnalyticsServiceDep,
) -> StudentProgressOverviewResponse:
    data = await service.student_progress_overview(
        cohort_id=cohort_id,
        membership_id=membership_id,
    )
    return StudentProgressOverviewResponse.model_validate(data)
