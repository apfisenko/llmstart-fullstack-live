from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from app.infrastructure.llm_assistant import LlmAssistant, LlmInvocationError

logger = logging.getLogger(__name__)

# Скользящее окно реплик (user+assistant), без БД — временный режим.
_MAX_MESSAGES = 40


class GuestDialogueService:
    def __init__(self, llm: LlmAssistant) -> None:
        self._llm = llm
        self._sessions: dict[str, list[tuple[str, str]]] = {}

    async def post_message(self, *, guest_session_key: str, content: str) -> dict:
        key = guest_session_key.strip()
        if key not in self._sessions:
            self._sessions[key] = []

        messages = self._sessions[key]
        snapshot = list(messages)
        messages.append(("user", content))
        if len(messages) > _MAX_MESSAGES:
            self._sessions[key] = messages[-_MAX_MESSAGES:]
            messages = self._sessions[key]

        logger.info(
            "guest_dialogue_message guest_key_len=%s content_len=%s",
            len(key),
            len(content),
        )

        try:
            assistant_text = await self._llm.reply(messages)
        except LlmInvocationError:
            self._sessions[key] = snapshot
            raise
        except Exception as exc:
            self._sessions[key] = snapshot
            logger.exception("guest_llm_unexpected_error")
            raise LlmInvocationError(str(exc)) from exc

        messages.append(("assistant", assistant_text))
        if len(messages) > _MAX_MESSAGES:
            self._sessions[key] = messages[-_MAX_MESSAGES:]

        created = datetime.now(timezone.utc)
        return {
            "assistant_message": {
                "id": uuid4(),
                "content": assistant_text,
                "created_at": created.isoformat().replace("+00:00", "Z"),
            }
        }

    def reset(self, guest_session_key: str) -> None:
        key = guest_session_key.strip()
        self._sessions.pop(key, None)
        logger.info("guest_dialogue_reset guest_key_len=%s", len(key))
