from fastapi import APIRouter, Depends

from app.api.deps import AuthServiceDep, require_client_token_if_configured
from app.api.v1.schemas_frontend import PostAuthDevSessionRequest, PostAuthDevSessionResponse

router = APIRouter(dependencies=[Depends(require_client_token_if_configured)])


@router.post("/auth/dev-session", response_model=PostAuthDevSessionResponse)
async def post_auth_dev_session(
    body: PostAuthDevSessionRequest,
    service: AuthServiceDep,
) -> PostAuthDevSessionResponse:
    data = await service.dev_session(body.telegram_username)
    return PostAuthDevSessionResponse.model_validate(data)
