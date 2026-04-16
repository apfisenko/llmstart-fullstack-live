from __future__ import annotations

import logging
from typing import Any, Optional
from uuid import UUID

import httpx

from bot.config import Config
from bot.utils.logger import hash_chat_id

logger = logging.getLogger(__name__)

_GUEST_MESSAGES_PATH = "/api/v1/assistant/guest/messages"
_GUEST_RESET_PATH = "/api/v1/assistant/guest/reset"


class BackendAssistantService:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._dialogue_ids: dict[int, UUID] = {}
        headers: dict[str, str] = {}
        token = config.backend_api_client_token.strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        backend_proxy = config.backend_http_proxy.strip() or None
        self._client = httpx.AsyncClient(
            base_url=config.resolved_backend_base_url(),
            headers=headers,
            proxy=backend_proxy,
            timeout=httpx.Timeout(config.backend_request_timeout),
            trust_env=False,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    def _messages_path(self) -> str:
        cid = self._config.cohort_id
        assert cid is not None
        return f"/api/v1/cohorts/{cid}/dialogues/messages"

    def _backend_ids_configured(self) -> bool:
        return self._config.cohort_id is not None and self._config.membership_id is not None

    def _guest_session_key(self, chat_id: int) -> str:
        return str(chat_id)

    def _extract_reply(self, data: dict[str, Any], ch: str) -> Optional[str]:
        assistant = data.get("assistant_message") or {}
        content = assistant.get("content")
        if not content:
            logger.error("backend_empty_assistant chat_hash=%s", ch)
            return None
        logger.info("backend_reply chat_hash=%s len=%s", ch, len(content))
        return str(content)

    async def chat(self, chat_id: int, text: str) -> str:
        ch = hash_chat_id(chat_id)
        if self._backend_ids_configured():
            return await self._chat_cohort(chat_id, text, ch)
        return await self._chat_guest(chat_id, text, ch)

    async def _chat_guest(self, chat_id: int, text: str, ch: str) -> str:
        body = {
            "guest_session_key": self._guest_session_key(chat_id),
            "content": text,
        }
        try:
            response = await self._client.post(_GUEST_MESSAGES_PATH, json=body)
        except httpx.RequestError:
            logger.exception("backend_guest_request_error chat_hash=%s", ch)
            return "Не удалось связаться с сервером. Попробуйте позже."

        if response.is_success:
            reply = self._extract_reply(response.json(), ch)
            if reply is None:
                return "Не удалось получить ответ. Попробуйте позже."
            return reply
        return self._map_error_response(response, ch)

    async def _chat_cohort(self, chat_id: int, text: str, ch: str) -> str:
        dialogue_id = self._dialogue_ids.get(chat_id)
        body: dict[str, Any] = {
            "membership_id": str(self._config.membership_id),
            "channel": "telegram",
            "content": text,
        }
        if dialogue_id is not None:
            body["dialogue_id"] = str(dialogue_id)

        try:
            response = await self._client.post(self._messages_path(), json=body)
        except httpx.RequestError:
            logger.exception("backend_request_error chat_hash=%s", ch)
            return "Не удалось связаться с сервером. Попробуйте позже."

        if response.is_success:
            data = response.json()
            new_id_raw = data.get("dialogue_id")
            if new_id_raw:
                self._dialogue_ids[chat_id] = UUID(str(new_id_raw))
            reply = self._extract_reply(data, ch)
            if reply is None:
                return "Не удалось получить ответ. Попробуйте позже."
            return reply

        return self._map_error_response(response, ch)

    async def lookup_dev_session(self, telegram_username: str, ch: str) -> str:
        """POST /api/v1/auth/dev-session — только отображение; бизнес-логика на backend."""
        token = self._config.backend_api_client_token.strip()
        if not token:
            logger.warning("dev_session_no_client_token chat_hash=%s", ch)
            return "Не задан BACKEND_API_CLIENT_TOKEN для запросов к API."

        raw = telegram_username.strip().lstrip("@")
        if not raw:
            return "Username пустой."

        body = {"telegram_username": raw}
        try:
            response = await self._client.post("/api/v1/auth/dev-session", json=body)
        except httpx.RequestError:
            logger.exception("dev_session_request_error chat_hash=%s", ch)
            return "Не удалось связаться с сервером."

        if response.status_code == 404:
            logger.info("dev_session_not_found chat_hash=%s username_len=%s", ch, len(raw))
            return "Пользователь с таким username не найден в базе."
        if response.status_code == 401:
            logger.warning("dev_session_unauthorized chat_hash=%s", ch)
            return "Нет доступа к API (проверьте токен клиента)."
        if not response.is_success:
            return self._map_error_response(response, ch)

        try:
            data = response.json()
        except ValueError:
            logger.error("dev_session_bad_json chat_hash=%s", ch)
            return "Некорректный ответ сервера."

        memberships = data.get("memberships") or []
        if not isinstance(memberships, list) or len(memberships) == 0:
            return "У пользователя нет участий в потоках."

        lines = ["Контекст по username (dev-session):"]
        display = data.get("display_name")
        if display:
            lines.append(f"Имя: {display}")
        lines.append(f"Участий: {len(memberships)}")
        for item in memberships[:8]:
            if not isinstance(item, dict):
                continue
            role = item.get("role", "?")
            title = item.get("cohort_title") or "—"
            lines.append(f"· {role}: {title}")
        if len(memberships) > 8:
            lines.append("…")
        lines.append("Веб-кабинет: см. README (frontend/web), вход по тому же username.")
        return "\n".join(lines)

    async def reset_history(self, chat_id: int) -> None:
        ch = hash_chat_id(chat_id)
        if not self._backend_ids_configured():
            await self._reset_guest(chat_id, ch)
            return
        await self._reset_cohort(chat_id, ch)

    async def _reset_guest(self, chat_id: int, ch: str) -> None:
        body = {"guest_session_key": self._guest_session_key(chat_id)}
        try:
            response = await self._client.post(_GUEST_RESET_PATH, json=body)
        except httpx.RequestError:
            logger.exception("backend_guest_reset_request_error chat_hash=%s", ch)
            return
        if not response.is_success:
            logger.warning(
                "guest_reset_unexpected_status chat_hash=%s status=%s",
                ch,
                response.status_code,
            )

    async def _reset_cohort(self, chat_id: int, ch: str) -> None:
        dialogue_id = self._dialogue_ids.get(chat_id)
        if dialogue_id is None:
            logger.warning("reset_no_dialogue chat_hash=%s", ch)
            return
        path = f"/api/v1/dialogues/{dialogue_id}/reset"
        try:
            response = await self._client.post(path)
        except httpx.RequestError:
            logger.exception("backend_reset_request_error chat_hash=%s", ch)
            return
        if response.status_code == 404:
            self._dialogue_ids.pop(chat_id, None)
            logger.warning("reset_dialogue_not_found chat_hash=%s", ch)
            return
        if response.is_success:
            self._dialogue_ids.pop(chat_id, None)
            return
        logger.warning(
            "reset_unexpected_status chat_hash=%s status=%s",
            ch,
            response.status_code,
        )

    def _map_error_response(self, response: httpx.Response, ch: str) -> str:
        code = response.status_code
        msg: Optional[str] = None
        try:
            payload = response.json()
            err = payload.get("error")
            if isinstance(err, dict) and err.get("message"):
                msg = str(err["message"])
        except (ValueError, TypeError):
            pass

        if code in (401, 403):
            logger.warning("backend_auth_error chat_hash=%s status=%s", ch, code)
            return "Нет доступа к сервису. Обратитесь к администратору."
        if code == 404:
            logger.warning("backend_not_found chat_hash=%s", ch)
            return "Данные для чата не найдены. Проверьте настройки бота (cohort / membership)."
        if code in (502, 503):
            logger.warning("backend_llm_error chat_hash=%s status=%s", ch, code)
            return "Не удалось получить ответ. Попробуйте позже."
        if code == 422:
            logger.warning("backend_validation_error chat_hash=%s", ch)
            return "Сообщение не принято. Попробуйте изменить текст."

        logger.warning(
            "backend_error chat_hash=%s status=%s detail=%s",
            ch,
            code,
            msg,
        )
        return "Произошла ошибка при обработке сообщения. Попробуйте позже."
