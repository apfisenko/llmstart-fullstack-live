from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models import CohortMembership, User


def normalize_telegram_username(raw: str) -> str:
    s = raw.strip()
    if s.startswith("@"):
        s = s[1:]
    return s.lower()


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_username(self, normalized: str) -> User | None:
        return await self._session.scalar(
            select(User)
            .where(func.lower(User.telegram_username) == normalized)
            .limit(1)
        )

    async def user_with_memberships(self, user_id) -> User | None:
        stmt = (
            select(User)
            .options(
                selectinload(User.memberships).selectinload(CohortMembership.cohort),
            )
            .where(User.id == user_id)
        )
        return await self._session.scalar(stmt)
