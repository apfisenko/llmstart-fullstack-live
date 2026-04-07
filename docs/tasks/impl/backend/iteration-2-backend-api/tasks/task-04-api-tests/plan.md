# Задача 04: Базовые API-тесты (паритет с ботом)

**Итерация:** 2 — Backend API  
**Статус:** Done  
**Дата:** 2026-04-07

---

## Цель

HTTP-автотесты для сценариев, паритетных текущему боту: отправка сообщения в диалог (LLM на стороне backend) и сброс контекста. Мок LLM, без PostgreSQL и без реальных вызовов OpenRouter/Telegram.

---

## Инвентаризация «бот → API»

| Поведение бота | HTTP API (v1) |
|----------------|---------------|
| Текст не-команда → ответ LLM | `POST /api/v1/cohorts/{cohort_id}/dialogues/messages` |
| `/reset` | `POST /api/v1/dialogues/{dialogue_id}/reset` |
| `/start`, `/help`, не-текст | Нет паритета на backend (клиент) |

Контракт: [docs/api/openapi-v1.yaml](../../../../../../api/openapi-v1.yaml).

---

## Решения

| Тема | Решение |
|------|---------|
| **Auth** | `BACKEND_API_CLIENT_TOKEN`: если задан — обязателен корректный `Authorization: Bearer`; если не задан — маршруты v1 без проверки (локальная разработка). В pytest через `monkeypatch` токен всегда задан. |
| **Реализация v1** | Минимальная in-memory логика диалога только для зелёных тестов; персистентность и прогресс — задача 05. |
| **LLM** | Протокол/класс в `app/infrastructure/`, подмена через `app.dependency_overrides` в тестах. |
| **422 vs ErrorResponse** | Пока стандартное тело FastAPI/Pydantic для 422; выравнивание с `ErrorResponse` — задача 05. |
| **Reset** | По `dialogue_id` очищается история сообщений в памяти; повторный reset — 204 (идемпотентно). |
| **Makefile** | Добавлена цель `test-backend` (корень репо); унификация `lint`/`test` для всего монорепо — задача 08. |

---

## Состав работ (план → факт)

- [x] Инвентаризация (таблица выше) — зафиксирована в этом файле
- [x] `pytest`, `httpx`, `pytest-asyncio`; `backend/tests/`, `conftest.py`
- [x] Маршруты `POST .../messages`, `POST .../reset` + тесты (happy, 422, 401, LLM failure, reset, caplog, health)
- [x] `backend/README.md`, `backend/.env.example`, корневой `Makefile`, `tasklist-backend.md`, `summary.md`

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `pytest` успешен без сети | `cd backend && uv sync --extra dev && uv run pytest` |
| 2 | Нет реального OpenRouter/Telegram | Моки / заглушки в коде и overrides |
| 3 | Воспроизводимо по README | Раздел «Тесты» в `backend/README.md` |

---

## Вне scope (задача 05)

`progress-checkpoints`, `progress-records`, `summary`, БД, строгая связь membership↔cohort, единый формат всех ошибок.

---

## Ссылки

- [Summary](summary.md)
- [OpenAPI](../../../../../../api/openapi-v1.yaml)
