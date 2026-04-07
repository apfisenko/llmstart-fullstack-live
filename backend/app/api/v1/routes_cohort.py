from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import CohortServiceDep, require_client_token_if_configured
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
