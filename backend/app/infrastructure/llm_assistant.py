from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Protocol, runtime_checkable

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)


class LlmInvocationError(Exception):
    """Сбой вызова LLM: маппится в 502/503 на HTTP-слое."""

    def __init__(
        self,
        message: str = "Assistant is temporarily unavailable",
        *,
        http_status: int = 503,
        error_code: str = "LLM_UNAVAILABLE",
    ) -> None:
        self.message = message
        self.http_status = http_status
        self.error_code = error_code
        super().__init__(message)


@runtime_checkable
class LlmAssistant(Protocol):
    async def reply(self, turns: list[tuple[str, str]]) -> str:
        """turns — пары (role, content), role в user|assistant."""


class StubLlmAssistant:
    async def reply(self, turns: list[tuple[str, str]]) -> str:
        if not turns:
            return "Hello."
        _role, last_user = turns[-1]
        return f"Echo:{len(last_user)}"


def normalize_completion_message_content(message: dict) -> str:
    """Достать текст из OpenAI-совместимого `choice.message` (`content` строка или список блоков)."""
    raw = message.get("content")
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw
    if isinstance(raw, list):
        parts: list[str] = []
        for block in raw:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                t = block.get("text")
                if isinstance(t, str):
                    parts.append(t)
                elif isinstance(block.get("content"), str):
                    parts.append(block["content"])
        return "".join(parts)
    return ""


def _text_from_reasoning_details(details: object) -> str:
    if not isinstance(details, list):
        return ""
    chunks: list[str] = []
    for item in details:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "reasoning.encrypted":
            continue
        t = item.get("text")
        if isinstance(t, str) and t.strip():
            chunks.append(t.strip())
        summ = item.get("summary")
        if isinstance(summ, str) and summ.strip():
            chunks.append(summ.strip())
    return "\n\n".join(chunks).strip()


def extract_assistant_text_from_choice(choice: dict) -> str:
    """
    Текст ответа ассистента из элемента `choices[]` (OpenRouter / OpenAI chat.completions).

    У reasoning-моделей `message.content` может быть пустым, а текст — в `reasoning` /
    `reasoning_details` (см. OpenRouter OpenAPI: ChatAssistantMessage).
    """
    msg = choice.get("message")
    if isinstance(msg, dict):
        body = normalize_completion_message_content(msg)
        if body.strip():
            return body

        r = msg.get("reasoning")
        if isinstance(r, str) and r.strip():
            return r.strip()

        alt = _text_from_reasoning_details(msg.get("reasoning_details"))
        if alt:
            return alt

        refusal = msg.get("refusal")
        if isinstance(refusal, str) and refusal.strip():
            return refusal.strip()

    legacy = choice.get("text")
    if isinstance(legacy, str) and legacy.strip():
        return legacy.strip()

    return ""


def load_system_prompt(settings: Settings) -> str:
    candidates = [
        Path(settings.system_prompt_path),
        Path(__file__).resolve().parents[3] / settings.system_prompt_path,
    ]
    for c in candidates:
        try:
            resolved = c.resolve()
        except OSError:
            continue
        if resolved.is_file():
            return resolved.read_text(encoding="utf-8")
    logger.warning("system_prompt_missing path=%s", settings.system_prompt_path)
    return "You are a helpful course assistant."


class OpenRouterLlmAssistant:
    def __init__(self, settings: Settings, http_client: httpx.AsyncClient) -> None:
        self._settings = settings
        self._http = http_client
        self._system_prompt = load_system_prompt(settings)

    async def reply(self, turns: list[tuple[str, str]]) -> str:
        key = self._settings.openrouter_api_key
        if not key:
            raise LlmInvocationError(
                "Assistant is not configured",
                http_status=503,
                error_code="LLM_UNAVAILABLE",
            )

        messages: list[dict[str, str]] = [{"role": "system", "content": self._system_prompt}]
        for role, content in turns:
            if role not in ("user", "assistant"):
                continue
            messages.append({"role": role, "content": content})

        base = self._settings.openrouter_base_url.rstrip("/")
        url = f"{base}/chat/completions"
        payload = {
            "model": self._settings.openrouter_model,
            "messages": messages,
        }
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

        try:
            response = await self._http.post(url, json=payload, headers=headers)
        except httpx.TimeoutException as exc:
            logger.warning("llm_timeout")
            raise LlmInvocationError(
                http_status=503,
                error_code="LLM_UNAVAILABLE",
            ) from exc
        except httpx.RequestError as exc:
            logger.warning("llm_request_error type=%s", type(exc).__name__)
            raise LlmInvocationError(
                http_status=503,
                error_code="LLM_UNAVAILABLE",
            ) from exc

        if response.status_code >= 500:
            logger.warning("llm_upstream_5xx status=%s", response.status_code)
            raise LlmInvocationError(http_status=503, error_code="LLM_UNAVAILABLE")

        if response.status_code == 429:
            logger.warning("llm_rate_limited")
            raise LlmInvocationError(http_status=503, error_code="LLM_UNAVAILABLE")

        if response.status_code >= 400:
            hint = ""
            try:
                data = response.json()
                err = data.get("error")
                if isinstance(err, dict):
                    hint = str(err.get("message") or err.get("code") or "")[:240]
                elif isinstance(err, str):
                    hint = err[:240]
            except (json.JSONDecodeError, TypeError, ValueError):
                hint = (response.text or "")[:240]
            logger.warning(
                "llm_upstream_4xx status=%s hint=%s",
                response.status_code,
                hint or "(no body)",
            )
            raise LlmInvocationError(http_status=502, error_code="LLM_BAD_GATEWAY")

        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            logger.warning("llm_invalid_json")
            raise LlmInvocationError(
                http_status=502,
                error_code="LLM_BAD_GATEWAY",
            ) from exc

        try:
            choice = data["choices"][0]
        except (KeyError, IndexError, TypeError) as exc:
            logger.warning("llm_malformed_response")
            raise LlmInvocationError(
                http_status=502,
                error_code="LLM_BAD_GATEWAY",
            ) from exc

        if not isinstance(choice, dict):
            logger.warning("llm_choice_not_object type=%s", type(choice).__name__)
            raise LlmInvocationError(http_status=502, error_code="LLM_BAD_GATEWAY")

        content = extract_assistant_text_from_choice(choice)
        if not content.strip():
            msg = choice.get("message")
            keys = sorted(msg.keys()) if isinstance(msg, dict) else None
            logger.warning(
                "llm_empty_or_unparsed_content choice_keys=%s message_keys=%s finish_reason=%s",
                sorted(choice.keys()),
                keys,
                choice.get("finish_reason"),
            )
            raise LlmInvocationError(http_status=502, error_code="LLM_BAD_GATEWAY")

        return content
