from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated, Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.errors import ApiError
from app.config import Settings, get_settings
from app.services.auth_service import AuthService
from app.services.cohort_analytics_service import CohortAnalyticsService
from app.services.cohort_service import CohortService
from app.services.dialogue_service import DialogueService
from app.services.guest_dialogue_service import GuestDialogueService

SettingsDep = Annotated[Settings, Depends(get_settings)]

_http_bearer = HTTPBearer(auto_error=False)


async def require_client_token_if_configured(
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials],
        Depends(_http_bearer),
    ],
    settings: SettingsDep,
) -> None:
    expected = settings.api_client_token
    if not expected:
        return
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(401, "UNAUTHORIZED", "Authentication required")
    if credentials.credentials != expected:
        raise ApiError(401, "UNAUTHORIZED", "Authentication required")


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_dialogue_service(
    session: SessionDep,
    request: Request,
    guest: GuestDialogueServiceDep,
) -> DialogueService:
    llm = request.app.state.llm
    return DialogueService(session, llm, guest)


def get_cohort_service(session: SessionDep) -> CohortService:
    return CohortService(session)


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


def get_cohort_analytics_service(session: SessionDep) -> CohortAnalyticsService:
    return CohortAnalyticsService(session)


def get_guest_dialogue_service(request: Request) -> GuestDialogueService:
    return request.app.state.guest_dialogue


DialogueServiceDep = Annotated[DialogueService, Depends(get_dialogue_service)]
CohortServiceDep = Annotated[CohortService, Depends(get_cohort_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CohortAnalyticsServiceDep = Annotated[CohortAnalyticsService, Depends(get_cohort_analytics_service)]
GuestDialogueServiceDep = Annotated[GuestDialogueService, Depends(get_guest_dialogue_service)]
