from __future__ import annotations

from uuid import UUID

from app.api.errors import ApiError
from app.domain.models import DialogueChannel, MembershipRole, MembershipStatus
from app.infrastructure.repositories.dialogue_repository import DialogueRepository
from app.infrastructure.repositories.user_repository import (
    UserRepository,
    normalize_telegram_username,
)


class AuthService:
    def __init__(self, session) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._dialogues = DialogueRepository(session)

    async def dev_session(self, telegram_username: str) -> dict:
        key = normalize_telegram_username(telegram_username)
        if not key:
            raise ApiError(422, "VALIDATION_ERROR", "telegram_username is empty")

        user = await self._users.get_by_telegram_username(key)
        if user is None:
            raise ApiError(404, "NOT_FOUND", "User not found")

        user = await self._users.user_with_memberships(user.id)
        assert user is not None

        memberships_out = []
        web_dialogue_id: UUID | None = None
        for m in user.memberships:
            if m.status != MembershipStatus.active:
                continue
            cohort = m.cohort
            memberships_out.append(
                {
                    "membership_id": m.id,
                    "cohort_id": m.cohort_id,
                    "cohort_title": cohort.title if cohort else None,
                    "role": m.role.value,
                }
            )
            if web_dialogue_id is None and m.role == MembershipRole.student:
                d = await self._dialogues.active_dialogue(
                    cohort_id=m.cohort_id,
                    membership_id=m.id,
                    channel=DialogueChannel.web,
                )
                if d is not None:
                    web_dialogue_id = d.id

        return {
            "user_id": user.id,
            "display_name": user.name,
            "memberships": memberships_out,
            "web_dialogue_id": web_dialogue_id,
        }
