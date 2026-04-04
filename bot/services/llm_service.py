import logging
from typing import Any

from openai import AsyncOpenAI

from bot.config import Config
from bot.utils.logger import hash_chat_id

logger = logging.getLogger(__name__)


class LlmService:
    def __init__(self, config: Config, system_prompt: str) -> None:
        self._config = config
        self._system_prompt = system_prompt
        self._history: dict[int, list[dict[str, str]]] = {}
        self._client = AsyncOpenAI(
            api_key=config.openrouter_api_key,
            base_url=config.openrouter_base_url,
            timeout=config.openrouter_timeout,
        )

    def reset_history(self, chat_id: int) -> None:
        self._history.pop(chat_id, None)

    def _trim(self, chat_id: int) -> None:
        messages = self._history.get(chat_id, [])
        max_size = self._config.max_history_size
        if len(messages) > max_size:
            self._history[chat_id] = messages[-max_size:]

    async def chat(self, chat_id: int, text: str) -> str:
        ch = hash_chat_id(chat_id)
        if chat_id not in self._history:
            self._history[chat_id] = []

        snapshot: list[dict[str, str]] = list(self._history[chat_id])
        messages = self._history[chat_id]
        messages.append({"role": "user", "content": text})
        self._trim(chat_id)

        api_messages: list[dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt},
            *messages,
        ]

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("LLM request chat_hash=%s messages_count=%s", ch, len(api_messages))

        try:
            response = await self._client.chat.completions.create(
                model=self._config.openrouter_model,
                messages=api_messages,
            )
            choice = response.choices[0]
            content = choice.message.content
            if not content:
                raise ValueError("Empty content from LLM")
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("LLM response chat_hash=%s reply_len=%s", ch, len(content))
            messages.append({"role": "assistant", "content": content})
            self._trim(chat_id)
            return content
        except Exception:
            self._history[chat_id] = snapshot
            logger.exception("LLM API error chat_hash=%s", ch)
            return "Не удалось получить ответ. Попробуйте позже."
