# Задача 04: Postgres в Docker, миграции, сид из progress-import, make

## Контекст

- **Схема и сид:** [`docs/data-model.md`](../../../../../../data-model.md), [`data/progress-import.v1.json`](../../../../../../../data/progress-import.v1.json).
- **Alembic:** [`backend/migrations/`](../../../../../../../backend/migrations/), цепочка на момент старта: `0001_initial` → `0002_user_name`.
- **ORM фактически расходится с целевой ER** (`dialogue_messages` vs `dialogue_turns` и др.) — сид строится на текущих моделях; выравнивание — задача 05.
- Источник DoD: [`docs/tasks/tasklist-database.md`](../../../../../../tasks/tasklist-database.md), блок 4.

## Цель

Воспроизводимое локальное окружение: PostgreSQL в Docker, цели `make db-*`, data-миграция импорта прогресса, проверочные SQL в справке.

## План работ

1. Добавить [`docker-compose.yml`](../../../../../../../docker-compose.yml) (postgres 16, volume, healthcheck).
2. Обновить [`backend/.env.example`](../../../../../../../backend/.env.example) при необходимости.
3. Расширить [`Makefile`](../../../../../../../Makefile): `db-up`, `db-down`, `db-reset`, `db-migrate`, `db-shell`; `migrate-backend` → синоним `db-migrate`; дефолтный `DATABASE_URL` под compose.
4. Ревизия Alembic **`0003_seed_progress`**: чтение JSON, вставка когорты, пользователей, членств, чекпоинтов, `progress_records` (`done` → `completed`, таймзона Moscow для naive `submitted_at`).
5. Обновить [`docs/tech/db-tooling-guide.md`](../../../../../../tech/db-tooling-guide.md): Docker, make, ревизия 0003, проверочные `SELECT`.
6. Самопроверка: `make db-reset`, `make db-shell`, запросы из справки (локально у разработчика).

## Критерии готовности (DoD)

См. блок 4 в [`tasklist-database.md`](../../../../../../tasks/tasklist-database.md).

## Связанные задачи

- **До:** задачи 01–03.
- **После:** задача 05 (ORM, репозитории, PostgreSQL в runtime backend).
