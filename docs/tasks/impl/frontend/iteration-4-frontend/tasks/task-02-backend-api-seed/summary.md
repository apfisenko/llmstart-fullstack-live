# Задача 02: итог

## Сделано

- **Схема:** миграции `0005` ( `telegram_username`, `is_homework`, `submission_links` ), `0006` (флаги ДЗ для импорта `hw_%`), `0007` (демо-сид).
- **ORM / API:** поля и эндпоинты по OpenAPI: `POST /auth/dev-session`, `GET` teacher-dashboard, leaderboard, progress-overview, `GET /dialogues/{id}/turns`, расширение `PUT` progress-records и чекпоинтов.
- **Сид `0007`:** идемпотентно по `cohorts.code = demo_frontend_mvp` — когорта «Demo cohort (frontend MVP)», преподаватель **`telegram_user_id` = 162684825**, **`telegram_username` = akozhin**, три студента с уникальными `telegram_username`, четыре чекпоинта (уроки + ДЗ), записи прогресса, два диалога (web + telegram) с ходами за последние дни.
- **Документация:** [`docs/tech/api-contracts.md`](../../../../../tech/api-contracts.md) и [`docs/api/openapi-v1.yaml`](../../../../../api/openapi-v1.yaml) — убраны отсылки «реализация — задача 02», зафиксирована политика лидерборда (опциональный `viewer_membership_id`: если есть — проверка членства в потоке; иначе MVP без проверки зрителя).
- **Makefile / README:** комментарий к `db-migrate-all` и абзац в README про демо-данные после миграций.

## Отклонения / решения

- **Лидерборд:** публичный режим в MVP — без обязательного `viewer_membership_id`; при передаче — только проверка, что участие из этого потока (не обязательно teacher).
- **Teacher-dashboard:** KPI и активность по **студентам** потока (исключены реплики преподавателя из лент и счётчиков).
- **Сид:** отдельная data-migration Alembic вместо отдельной CLI-команды; `make db-migrate` / `db-up` уже поднимают цепочку до `0007`.

## Проверка

- `cd backend && uv run ruff check app tests`
- С PostgreSQL: `TEST_DATABASE_URL` на БД `*_test`, затем `uv run pytest tests/pg`
- Миграции: `make db-migrate` или `uv run alembic upgrade head` с нужным `DATABASE_URL`
