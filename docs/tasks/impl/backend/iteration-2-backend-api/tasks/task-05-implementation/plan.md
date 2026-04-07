# Задача 05 — Реализация endpoint'ов и персистентности

**Итерация:** 2 — Backend API  
**Статус:** выполнена (см. [summary.md](summary.md))

## Цель

Реализовать контракт v1: диалог с LLM на backend, прогресс и сводка потока; PostgreSQL + SQLAlchemy async + Alembic.

## Состав (фактический план работ)

1. Зависимости: `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `httpx`; dev: `psycopg2-binary`, `aiosqlite`.
2. `Settings.database_url` (обязательный), миграция `0001_initial`, `make migrate-backend`.
3. ORM-модели в `backend/app/domain/models.py` (enum в БД как строки, `native_enum=False`, тип `Uuid` для совместимости с SQLite в тестах).
4. `infrastructure/database.py`, `deps.get_db_session`, сервисы `DialogueService`, `CohortService`.
5. OpenRouter в `infrastructure/llm_assistant.py` при наличии ключа; иначе `StubLlmAssistant`; 502/503 по типу сбоя.
6. Маршруты cohort/progress; `GET .../summary` с query `viewer_membership_id` (MVP при общем Bearer).
7. Тесты: SQLite in-memory + `StaticPool`, фикстуры сидов; расширенный `test_api.py`.

## Связанные документы

- [tasklist-backend.md](../../../../../tasklist-backend.md)
- [api-contracts.md](../../../../tech/api-contracts.md)
