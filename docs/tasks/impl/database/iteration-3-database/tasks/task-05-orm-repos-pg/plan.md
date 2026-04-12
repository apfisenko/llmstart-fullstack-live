# Задача 05: ORM, репозитории, PostgreSQL

## Цель

Выровнять персистентность диалогов с [`docs/data-model.md`](../../../../../../data-model.md) (`dialogue_turns`), вынести доступ к данным в репозитории, сохранить сквозную работу API и тестов.

## Состав работ (факт плана)

1. ORM `DialogueTurn`, удаление `DialogueMessage` / `MessageRole`; связь `Dialogue.turns`.
2. Миграция `0004_dialogue_turns`: создание таблицы, перенос пар из `dialogue_messages` при наличии, удаление `dialogue_messages`; учёт пути «только create_all» на свежем `db-reset`.
3. `DialogueService` — одна вставка на пару Q/A; `reset` по `dialogue_turns`.
4. Репозитории: `DialogueRepository`, `CohortProgressRepository` в `backend/app/infrastructure/repositories/`.
5. Документация: OpenAPI, db-tooling-guide, api-contracts, блок в data-model; Makefile-алиасы `backend-test`, `backend-dev`, `backend-lint`, `backend-typecheck`.

## DoD

- Потоковый чат и прогресс в PostgreSQL; после рестарта данные не из памяти процесса (исключение: `GuestDialogueService` — гостевой режим).
- `make test-backend` / `make backend-test` — зелёные тесты.
- `make lint` / `make backend-lint` — без ошибок ruff.

## Исключения

- **mypy:** не подключён в `backend/pyproject.toml`; цель `make backend-typecheck` выводит пояснение (расширение — отдельная задача).
