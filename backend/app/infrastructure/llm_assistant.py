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
            logger.warning("llm_upstream_4xx status=%s", response.status_code)
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
            msg = choice["message"]
            content = msg["content"]
        except (KeyError, IndexError, TypeError) as exc:
            logger.warning("llm_malformed_response")
            raise LlmInvocationError(
                http_status=502,
                error_code="LLM_BAD_GATEWAY",
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise LlmInvocationError(http_status=502, error_code="LLM_BAD_GATEWAY")

        return content
