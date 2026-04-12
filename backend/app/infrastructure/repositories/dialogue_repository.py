from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models import (
    Cohort,
    CohortMembership,
    Dialogue,
    DialogueChannel,
    DialogueState,
    DialogueTurn,
)


class DialogueRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def cohort_exists(self, cohort_id: UUID) -> bool:
        found = await self._session.scalar(select(Cohort.id).where(Cohort.id == cohort_id))
        return found is not None

    async def membership_in_cohort(
        self, cohort_id: UUID, membership_id: UUID
    ) -> CohortMembership | None:
        return await self._session.scalar(
            select(CohortMembership).where(
                CohortMembership.id == membership_id,
                CohortMembership.cohort_id == cohort_id,
            )
        )

    async def dialogue_with_membership(self, dialogue_id: UUID) -> Dialogue | None:
        return await self._session.scalar(
            select(Dialogue)
            .options(selectinload(Dialogue.membership))
            .where(Dialogue.id == dialogue_id)
        )

    async def active_dialogue(
        self,
        *,
        cohort_id: UUID,
        membership_id: UUID,
        channel: DialogueChannel,
    ) -> Dialogue | None:
        return await self._session.scalar(
            select(Dialogue)
            .where(
                Dialogue.membership_id == membership_id,
                Dialogue.channel == channel,
                Dialogue.state == DialogueState.active,
            )
            .join(CohortMembership, Dialogue.membership_id == CohortMembership.id)
            .where(CohortMembership.cohort_id == cohort_id)
        )

    async def ordered_turns(self, dialogue_id: UUID) -> list[DialogueTurn]:
        stmt = (
            select(DialogueTurn)
            .where(DialogueTurn.dialogue_id == dialogue_id)
            .order_by(DialogueTurn.asked_at, DialogueTurn.id)
        )
        return list((await self._session.scalars(stmt)).all())

    def add_turn(self, turn: DialogueTurn) -> None:
        self._session.add(turn)

    def add_dialogue(self, dialogue: Dialogue) -> None:
        self._session.add(dialogue)

    async def delete_turns(self, dialogue_id: UUID) -> None:
        await self._session.execute(
            delete(DialogueTurn).where(DialogueTurn.dialogue_id == dialogue_id)
        )

    async def dialogue_exists(self, dialogue_id: UUID) -> bool:
        found = await self._session.scalar(select(Dialogue.id).where(Dialogue.id == dialogue_id))
        return found is not None
