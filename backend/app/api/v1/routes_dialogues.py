from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import DialogueServiceDep, require_client_token_if_configured
from app.api.errors import ApiError
from app.api.v1.schemas_dialogues import (
    PostDialogueMessageRequest,
    PostDialogueMessageResponse,
)
from app.api.v1.schemas_frontend import DialogueTurnsListResponse

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


def _parse_before_asked_at(raw: Optional[str]) -> Optional[datetime]:
    if raw is None or raw == "":
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ApiError(422, "VALIDATION_ERROR", "Invalid before_asked_at") from exc


@router.get(
    "/dialogues/{dialogue_id}/turns",
    response_model=DialogueTurnsListResponse,
)
async def list_dialogue_turns(
    dialogue_id: UUID,
    service: DialogueServiceDep,
    limit: int = Query(20, ge=1, le=100),
    before_asked_at: Optional[str] = Query(None),
) -> DialogueTurnsListResponse:
    data = await service.list_turns(
        dialogue_id=dialogue_id,
        before_asked_at=_parse_before_asked_at(before_asked_at),
        limit=limit,
    )
    return DialogueTurnsListResponse.model_validate(data)
