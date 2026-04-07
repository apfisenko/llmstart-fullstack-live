from __future__ import annotations

import logging
from datetime import timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.api.errors import ApiError
from app.domain.models import (
    CohortMembership,
    Dialogue,
    DialogueChannel,
    DialogueMessage,
    DialogueState,
    MessageRole,
)
from app.infrastructure.llm_assistant import LlmAssistant, LlmInvocationError

logger = logging.getLogger(__name__)


class DialogueService:
    def __init__(self, session, llm: LlmAssistant) -> None:
        self._session = session
        self._llm = llm

    async def post_message(
        self,
        *,
        cohort_id: UUID,
        membership_id: UUID,
        channel: str,
        dialogue_id: Optional[UUID],
        content: str,
    ) -> dict:
        membership = await self._session.scalar(
            select(CohortMembership).where(
                CohortMembership.id == membership_id,
                CohortMembership.cohort_id == cohort_id,
            )
        )
        if membership is None:
            raise ApiError(404, "NOT_FOUND", "Membership not found")

        ch = DialogueChannel(channel)

        if dialogue_id is not None:
            dialogue = await self._session.scalar(
                select(Dialogue)
                .options(selectinload(Dialogue.membership))
                .where(Dialogue.id == dialogue_id)
            )
            if dialogue is None:
                raise ApiError(404, "NOT_FOUND", "Dialogue not found")
            if dialogue.membership_id != membership_id:
                raise ApiError(403, "FORBIDDEN", "Forbidden")
            if dialogue.membership.cohort_id != cohort_id:
                raise ApiError(403, "FORBIDDEN", "Forbidden")
        else:
            dialogue = await self._session.scalar(
                select(Dialogue)
                .where(
                    Dialogue.membership_id == membership_id,
                    Dialogue.channel == ch,
                    Dialogue.state == DialogueState.active,
                )
                .join(CohortMembership, Dialogue.membership_id == CohortMembership.id)
                .where(CohortMembership.cohort_id == cohort_id)
            )
            if dialogue is None:
                dialogue = Dialogue(
                    id=uuid4(),
                    membership_id=membership_id,
                    channel=ch,
                    state=DialogueState.active,
                )
                self._session.add(dialogue)
                await self._session.flush()

        stmt = (
            select(DialogueMessage)
            .where(DialogueMessage.dialogue_id == dialogue.id)
            .order_by(DialogueMessage.created_at)
        )
        existing = (await self._session.scalars(stmt)).all()
        turns: list[tuple[str, str]] = []
        for m in existing:
            if m.role in (MessageRole.user, MessageRole.assistant):
                turns.append((m.role.value, m.content))
        turns.append(("user", content))

        user_message = DialogueMessage(
            id=uuid4(),
            dialogue_id=dialogue.id,
            role=MessageRole.user,
            content=content,
        )
        self._session.add(user_message)
        await self._session.flush()

        logger.info(
            "dialogue_message cohort_id=%s dialogue_id=%s content_len=%s",
            cohort_id,
            dialogue.id,
            len(content),
        )

        try:
            assistant_text = await self._llm.reply(turns)
        except LlmInvocationError:
            raise
        except Exception as exc:
            logger.exception("llm_unexpected_error")
            raise LlmInvocationError(str(exc)) from exc

        assistant_message = DialogueMessage(
            id=uuid4(),
            dialogue_id=dialogue.id,
            role=MessageRole.assistant,
            content=assistant_text,
        )
        self._session.add(assistant_message)
        await self._session.flush()

        created_at = assistant_message.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        return {
            "dialogue_id": dialogue.id,
            "user_message_id": user_message.id,
            "assistant_message": {
                "id": assistant_message.id,
                "content": assistant_text,
                "created_at": created_at.isoformat().replace("+00:00", "Z"),
            },
        }

    async def reset(self, dialogue_id: UUID) -> None:
        dialogue = await self._session.scalar(select(Dialogue).where(Dialogue.id == dialogue_id))
        if dialogue is None:
            raise ApiError(404, "NOT_FOUND", "Dialogue not found")
        await self._session.execute(
            delete(DialogueMessage).where(DialogueMessage.dialogue_id == dialogue_id)
        )
        logger.info("dialogue_reset dialogue_id=%s", dialogue_id)
