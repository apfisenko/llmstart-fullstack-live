from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import DialogueServiceDep, require_client_token_if_configured
from app.api.v1.schemas_dialogues import (
    PostDialogueMessageRequest,
    PostDialogueMessageResponse,
)

router = APIRouter(dependencies=[Depends(require_client_token_if_configured)])


@router.post(
    "/cohorts/{cohort_id}/dialogues/messages",
    response_model=PostDialogueMessageResponse,
)
async def post_cohort_dialogue_message(
    cohort_id: UUID,
    body: PostDialogueMessageRequest,
    service: DialogueServiceDep,
) -> PostDialogueMessageResponse:
    result = await service.post_message(
        cohort_id=cohort_id,
        membership_id=body.membership_id,
        channel=body.channel.value,
        dialogue_id=body.dialogue_id,
        content=body.content,
    )
    return PostDialogueMessageResponse.model_validate(result)


@router.post("/dialogues/{dialogue_id}/reset", status_code=204)
async def post_dialogue_reset(
    dialogue_id: UUID,
    service: DialogueServiceDep,
) -> None:
    await service.reset(dialogue_id)
