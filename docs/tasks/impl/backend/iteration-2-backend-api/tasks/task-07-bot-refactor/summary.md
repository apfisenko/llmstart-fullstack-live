# Задача 07: summary

**Статус:** Done  
**Дата:** 2026-04-07

## Факт

- Удалён прямой вызов OpenRouter из бота (`bot/services/llm_service.py`); добавлен [`bot/services/backend_assistant.py`](../../../../../../../bot/services/backend_assistant.py) с `httpx.AsyncClient`.
- [`bot/config.py`](../../../../../../../bot/config.py): обязательны `cohort_id`, `membership_id`; URL backend из `BACKEND_BASE_URL` или `BACKEND_HOST`/`BACKEND_PORT`; опционально токен клиента и таймаут.
- Handlers и [`bot/main.py`](../../../../../../../bot/main.py) переведены на новый сервис; `/reset` вызывает `await reset_history` (HTTP reset + сброс локального `dialogue_id`).
- Корневые [`pyproject.toml`](../../../../../../../pyproject.toml), [`requirements.txt`](../../../../../../../requirements.txt): `httpx` вместо `openai`; обновлён [`uv.lock`](../../../../../../../uv.lock).
- Документация: [`.env.example`](../../../../../../../.env.example), [`README.md`](../../../../../../../README.md) (порядок: backend → демо-SQL для SQLite → бот), [`docs/integrations.md`](../../../../../../integrations.md), [`docs/plan.md`](../../../../../../plan.md), [`.cursor/rules/conventions.mdc`](../../../../../../../.cursor/rules/conventions.mdc).

## Отклонения

- Нет: по плану.

## Ограничения MVP

- Один `MEMBERSHIP_ID` в `.env` для всех чатов Telegram; привязка Telegram user ↔ membership — вне scope.
