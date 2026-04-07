# Задача 05 — Summary

**Итерация:** 2 — Backend API  
**Статус:** Done  
**Дата:** 2026-04-07

## Что сделано

1. **PostgreSQL (прод):** `DATABASE_URL` (`postgresql+asyncpg://...`), Alembic [`backend/migrations/versions/0001_initial_schema.py`](../../../../../../../backend/migrations/versions/0001_initial_schema.py), цель [`Makefile`](../../../../../../../Makefile) `migrate-backend`.
2. **ORM:** [`backend/app/domain/models.py`](../../../../../../../backend/app/domain/models.py) — сущности по `data-model.md`; UUID через `sqlalchemy.Uuid`; перечисления `native_enum=False` (VARCHAR в Postgres и SQLite).
3. **HTTP:** диалог — [`DialogueService`](../../../../../../../backend/app/services/dialogue_service.py), прогресс/summary — [`CohortService`](../../../../../../../backend/app/services/cohort_service.py), роуты — [`routes_dialogues.py`](../../../../../../../backend/app/api/v1/routes_dialogues.py), [`routes_cohort.py`](../../../../../../../backend/app/api/v1/routes_cohort.py).
4. **LLM:** [`OpenRouterLlmAssistant`](../../../../../../../backend/app/infrastructure/llm_assistant.py), ошибки **502** `LLM_BAD_GATEWAY` / **503** `LLM_UNAVAILABLE`; без ключа — заглушка.
5. **Контракт:** в OpenAPI и [`api-contracts.md`](../../../../../../tech/api-contracts.md) зафиксирован query **`viewer_membership_id`** для `GET .../summary` (идентификация преподавателя при общем Bearer).
6. **Документация:** [`docs/integrations.md`](../../../../../../integrations.md), [`backend/README.md`](../../../../../../../backend/README.md).
7. **Тесты:** pytest по умолчанию на **SQLite** in-memory (`StaticPool`); сиды в [`conftest.py`](../../../../../../../backend/tests/conftest.py).

## Отклонения / допущения

- **Тесты без PostgreSQL:** локальный прогон `pytest` не требует Postgres; интеграция с реальной БД — через `DATABASE_URL` на Postgres + миграции.
- **PUT прогресса:** разрешён только для участия с ролью `student` (преподаватель получает **403**).
- **422:** формат тела по-прежнему стандартный FastAPI (`detail`), унификация под `ErrorResponse` не входила в объём 05.

## Ссылки

- [План](plan.md)
