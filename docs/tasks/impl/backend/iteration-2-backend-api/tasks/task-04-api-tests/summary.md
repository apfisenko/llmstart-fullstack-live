# Задача 04: Summary — Базовые API-тесты

**Итерация:** 2 — Backend API  
**Статус:** Done  
**Дата:** 2026-04-07

---

## Что сделано

1. Добавлены dev-зависимости в [`backend/pyproject.toml`](../../../../../../../backend/pyproject.toml): `pytest`, `pytest-asyncio`, `httpx`; секция `[tool.pytest.ini_options]` (`asyncio_mode = auto`).
2. Минимальные маршруты v1 под контракт диалога: [`POST .../cohorts/{cohort_id}/dialogues/messages`](../../../../../../../backend/app/api/v1/routes_dialogues.py), [`POST .../dialogues/{dialogue_id}/reset`](../../../../../../../backend/app/api/v1/routes_dialogues.py); in-memory в [`InMemoryDialogueService`](../../../../../../../backend/app/services/dialogue_service.py); заглушка LLM — [`StubLlmAssistant`](../../../../../../../backend/app/infrastructure/llm_assistant.py); опциональный Bearer — [`BACKEND_API_CLIENT_TOKEN`](../../../../../../../backend/app/config.py) + [`require_client_token_if_configured`](../../../../../../../backend/app/api/deps.py).
3. Обработчики ошибок: [`ApiError`](../../../../../../../backend/app/api/errors.py) (401/403/404 и т.д.), [`LlmInvocationError`](../../../../../../../backend/app/infrastructure/llm_assistant.py) → 503 `LLM_UNAVAILABLE` в [`main.py`](../../../../../../../backend/app/main.py).
4. Тесты: [`backend/tests/test_api.py`](../../../../../../../backend/tests/test_api.py), [`conftest.py`](../../../../../../../backend/tests/conftest.py) — happy path, 422, 401, сценарий без токена, сбой LLM, reset, caplog без текста пользователя, 403 при чужом `membership_id`.
5. Документация и команды: [`backend/README.md`](../../../../../../../backend/README.md), [`backend/.env.example`](../../../../../../../backend/.env.example), цель `make test-backend` в [`Makefile`](../../../../../../../Makefile).

---

## Отклонения от плана

- **`app.state.dialogue_service`** задаётся сразу в `create_app()`, а не в lifespan: транспорт `httpx.ASGITransport` в тестах не поднимал lifespan, из‑за чего `State` оставался без сервиса. Логирование по-прежнему в lifespan.
- Ответы **422** остаются в формате FastAPI/Pydantic (не обёртка `ErrorResponse`) — выравнивание в задаче 05.

---

## Ссылки

- [План](plan.md)
