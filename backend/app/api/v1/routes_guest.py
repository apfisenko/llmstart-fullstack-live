from fastapi import APIRouter, Depends

from app.api.deps import GuestDialogueServiceDep, require_client_token_if_configured
from app.api.v1.schemas_guest import (
    PostGuestMessageRequest,
    PostGuestMessageResponse,
    PostGuestResetRequest,
)

router = APIRouter(dependencies=[Depends(require_client_token_if_configured)])


@router.post(
    "/assistant/guest/messages",
    response_model=PostGuestMessageResponse,
)
async def post_guest_message(
    body: PostGuestMessageRequest,
    service: GuestDialogueServiceDep,
) -> PostGuestMessageResponse:
    result = await service.post_message(
        guest_session_key=body.guest_session_key,
        content=body.content,
    )
    return PostGuestMessageResponse.model_validate(result)


@router.post("/assistant/guest/reset", status_code=204)
async def post_guest_reset(
    body: PostGuestResetRequest,
    service: GuestDialogueServiceDep,
) -> None:
    service.reset(body.guest_session_key)
