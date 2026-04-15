from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from app.api.errors import ApiError
from app.domain.models import Dialogue, DialogueChannel, DialogueState, DialogueTurn
from app.infrastructure.llm_assistant import LlmAssistant, LlmInvocationError
from app.infrastructure.repositories.dialogue_repository import DialogueRepository
from app.services.guest_dialogue_service import GuestDialogueService

logger = logging.getLogger(__name__)

# Стабильный synthetic dialogue_id для режима «поток не в БД» (как гостевой LLM).
_EPHEMERAL_DIALOGUE_NS = UUID("018f3a2c-7b91-7d00-8000-000000000001")


class DialogueService:
    def __init__(self, session, llm: LlmAssistant, guest: GuestDialogueService) -> None:
        self._session = session
        self._llm = llm
        self._guest = guest
        self._dialogues = DialogueRepository(session)

    def _ephemeral_guest_key(self, cohort_id: UUID, membership_id: UUID, channel: str) -> str:
        return f"v1-cohort-missing:{cohort_id}:{membership_id}:{channel}"

    def _ephemeral_dialogue_id(self, cohort_id: UUID, membership_id: UUID, channel: str) -> UUID:
        return uuid.uuid5(
            _EPHEMERAL_DIALOGUE_NS,
            self._ephemeral_guest_key(cohort_id, membership_id, channel),
        )

    async def _post_message_cohort_not_in_db(
        self,
        *,
        cohort_id: UUID,
        membership_id: UUID,
        channel: str,
        dialogue_id: Optional[UUID],
        content: str,
    ) -> dict:
        expected_dialogue_id = self._ephemeral_dialogue_id(cohort_id, membership_id, channel)
        if dialogue_id is not None and dialogue_id != expected_dialogue_id:
            raise ApiError(403, "FORBIDDEN", "Forbidden")

        guest_key = self._ephemeral_guest_key(cohort_id, membership_id, channel)
        result = await self._guest.post_message(guest_session_key=guest_key, content=content)
        logger.info(
            "dialogue_message_ephemeral_cohort dialogue_id=%s content_len=%s",
            expected_dialogue_id,
            len(content),
        )
        return {
            "dialogue_id": expected_dialogue_id,
            "user_message_id": uuid4(),
            "assistant_message": result["assistant_message"],
        }

    async def post_message(
        self,
        *,
        cohort_id: UUID,
        membership_id: UUID,
        channel: str,
        dialogue_id: Optional[UUID],
        content: str,
    ) -> dict:
        if not await self._dialogues.cohort_exists(cohort_id):
            return await self._post_message_cohort_not_in_db(
                cohort_id=cohort_id,
                membership_id=membership_id,
                channel=channel,
                dialogue_id=dialogue_id,
                content=content,
            )

        membership = await self._dialogues.membership_in_cohort(cohort_id, membership_id)
        if membership is None:
            raise ApiError(404, "NOT_FOUND", "Membership not found")

        ch = DialogueChannel(channel)

        if dialogue_id is not None:
            dialogue = await self._dialogues.dialogue_with_membership(dialogue_id)
            if dialogue is None:
                raise ApiError(404, "NOT_FOUND", "Dialogue not found")
            if dialogue.membership_id != membership_id:
                raise ApiError(403, "FORBIDDEN", "Forbidden")
            if dialogue.membership.cohort_id != cohort_id:
                raise ApiError(403, "FORBIDDEN", "Forbidden")
        else:
            dialogue = await self._dialogues.active_dialogue(
                cohort_id=cohort_id,
                membership_id=membership_id,
                channel=ch,
            )
            if dialogue is None:
                dialogue = Dialogue(
                    id=uuid4(),
                    membership_id=membership_id,
                    channel=ch,
                    state=DialogueState.active,
                )
                self._dialogues.add_dialogue(dialogue)
                await self._session.flush()

        existing = await self._dialogues.ordered_turns(dialogue.id)
        turns: list[tuple[str, str]] = []
        for row in existing:
            turns.append(("user", row.question_text))
            turns.append(("assistant", row.answer_text))
        turns.append(("user", content))

        user_message_id = uuid4()
        assistant_message_id = uuid4()
        asked_at = datetime.now(timezone.utc)

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

        answered_at = datetime.now(timezone.utc)
        if answered_at < asked_at:
            answered_at = asked_at

        turn_row = DialogueTurn(
            id=user_message_id,
            assistant_message_id=assistant_message_id,
            dialogue_id=dialogue.id,
            question_text=content,
            answer_text=assistant_text,
            asked_at=asked_at,
            answered_at=answered_at,
        )
        self._dialogues.add_turn(turn_row)
        await self._session.flush()

        created_at = turn_row.answered_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        return {
            "dialogue_id": dialogue.id,
            "user_message_id": user_message_id,
            "assistant_message": {
                "id": assistant_message_id,
                "content": assistant_text,
                "created_at": created_at.isoformat().replace("+00:00", "Z"),
            },
        }

    async def reset(self, dialogue_id: UUID) -> None:
        if not await self._dialogues.dialogue_exists(dialogue_id):
            raise ApiError(404, "NOT_FOUND", "Dialogue not found")
        await self._dialogues.delete_turns(dialogue_id)
        logger.info("dialogue_reset dialogue_id=%s", dialogue_id)

    async def list_turns(
        self,
        *,
        dialogue_id: UUID,
        before_asked_at: Optional[datetime],
        limit: int,
    ) -> dict:
        if not await self._dialogues.dialogue_exists(dialogue_id):
            raise ApiError(404, "NOT_FOUND", "Dialogue not found")

        fetch_limit = min(max(limit, 1), 100) + 1
        rows_desc = await self._dialogues.list_turns_desc(
            dialogue_id, before_asked_at=before_asked_at, limit=fetch_limit
        )
        has_more = len(rows_desc) > fetch_limit - 1
        rows_desc = rows_desc[: fetch_limit - 1]
        rows_asc = list(reversed(rows_desc))

        items = [
            {
                "user_message_id": t.id,
                "assistant_message_id": t.assistant_message_id,
                "question_text": t.question_text,
                "answer_text": t.answer_text,
                "asked_at": t.asked_at.isoformat().replace("+00:00", "Z"),
                "answered_at": t.answered_at.isoformat().replace("+00:00", "Z"),
            }
            for t in rows_asc
        ]
        next_before = None
        if has_more and rows_asc:
            oldest = rows_asc[0].asked_at
            if oldest.tzinfo is None:
                oldest = oldest.replace(tzinfo=timezone.utc)
            next_before = oldest.isoformat().replace("+00:00", "Z")

        return {"items": items, "next_before_asked_at": next_before}
