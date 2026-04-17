# Задача 04: итог

## Сделано

- **[`docker-compose.yml`](../../../../../../../docker-compose.yml):** сервис `postgres`, образ `postgres:16-alpine`, учётка/БД `llmstart`, порт 5432, volume `llmstart_pg_data`, healthcheck `pg_isready`.
- **[`Makefile`](../../../../../../../Makefile):** `db-up` (`docker compose up -d --wait`), `db-down`, `db-reset` (down `-v` + up + миграции), `db-migrate`, `db-shell`; `DATABASE_URL` по умолчанию под compose; **`migrate-backend`** вызывает ту же логику, что **`db-migrate`**.
- **[`backend/migrations/versions/0003_seed_course_progress.py`](../../../../../../../backend/migrations/versions/0003_seed_course_progress.py):** импорт из [`data/progress-import.v1.json`](../../../../../../../data/progress-import.v1.json); идемпотентность по `cohorts.title`; `downgrade` удаляет данные сида и пользователей по списку `telegram_user_id` из JSON.
- **[`docs/tech/db-tooling-guide.md`](../../../../../../tech/db-tooling-guide.md):** разделы Docker, make, описание ревизии 0003, проверочные SQL после `db-reset`.
- **Примеры env:** [`backend/.env.example`](../../../../../../../backend/.env.example) (строка `DATABASE_URL` под локальный compose).

## Отклонения от формулировок tasklist

| Ожидание в tasklist | Факт |
|---------------------|------|
| Вторая миграция — сид `0002_seed_progress` | Сид — **третья** ревизия **`0003_seed_progress`**, т.к. `0002` уже занята [`0002_rename_users_display_name_to_name.py`](../../../../../../../backend/migrations/versions/0002_rename_users_display_name_to_name.py). |
| DoD: «24 progress со статусом `done`» | В БД и OpenAPI статус завершения — **`completed`**; в JSON импорта — `done`. Сид маппит в **`completed`**. |
| Проверка в среде агента | В CI/агенте Docker может быть недоступен; **`pytest`** — зелёный. Самопроверка Postgres (2026-04): `docker compose` в WSL, миграции с Windows-хоста через `uv run --env-file … alembic upgrade head`, ожидания DoD (13 / 3 / 24, `0003_seed_progress`) подтверждены скриптом [`scripts/pg-selftest.sql`](../../../../../../../scripts/pg-selftest.sql). На **Windows** для миграции **`0003`** в dev добавлен пакет **`tzdata`** (иначе `ZoneInfo("Europe/Moscow")` падает). Полный сценарий локально: см. [`docs/tech/db-tooling-guide.md`](../../../../../../tech/db-tooling-guide.md) (WSL + Docker, проверка после `upgrade head`). |

## Следующий шаг

Задача 05: ORM/репозитории и замена in-memory в сервисах; сближение схемы с [`docs/data-model.md`](../../../../../../data-model.md) при необходимости отдельными ревизиями после этой задачи.
