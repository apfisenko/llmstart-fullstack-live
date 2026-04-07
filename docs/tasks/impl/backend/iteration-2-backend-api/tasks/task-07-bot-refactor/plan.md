# Задача 07: рефакторинг бота под backend API

**Итерация:** 5 (интеграция клиентов), по [tasklist-backend](../../../../../../tasklist-backend.md)  
**Статус:** Done  
**Дата:** 2026-04-07

## Цель

Бот — тонкий клиент: `httpx` → backend `/api/v1/`, без OpenRouter и без in-memory истории реплик; допустим кэш `dialogue_id` по `chat_id`.

## Паритет (задача 04)

| Бот | API |
|-----|-----|
| Текст | `POST .../cohorts/{id}/dialogues/messages` |
| `/reset` | `POST .../dialogues/{dialogue_id}/reset` |

## Решения

| Тема | Решение |
|------|---------|
| URL backend | `BACKEND_BASE_URL` или `http://BACKEND_HOST:BACKEND_PORT` |
| Идентификация домена | Обязательные `COHORT_ID`, `MEMBERSHIP_ID` в `.env` (MVP: один участник на всех пользователей Telegram) |
| Auth | `BACKEND_API_CLIENT_TOKEN` → заголовок `Authorization: Bearer` при непустом значении |
| Сервис | `bot/services/backend_assistant.py`, `BackendAssistantService` |
| Зависимости | `openai` убран из корневого `pyproject.toml` / `requirements.txt`, добавлен `httpx` |

## Фиксация прогресса

В `bot/` нет обработчиков прогресса — не переводились на API в этой задаче.

## Ссылки

- [Summary](summary.md)
- [api-contracts.md](../../../../../../tech/api-contracts.md)
