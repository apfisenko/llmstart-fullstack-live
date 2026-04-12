# Задача 03: ADR операций с БД и справка по инструментам

## Контекст

- **Стек backend и ORM** уже принят: [`docs/adr/adr-002-backend-stack.md`](../../../../../../adr/adr-002-backend-stack.md).
- **СУБД:** [`docs/adr/adr-001-database.md`](../../../../../../adr/adr-001-database.md).
- **Схема и именование таблиц:** [`docs/data-model.md`](../../../../../../data-model.md).
- **Фактический код:** [`backend/migrations/env.py`](../../../../../../../backend/migrations/env.py), [`backend/alembic.ini`](../../../../../../../backend/alembic.ini), [`Makefile`](../../../../../../../Makefile).

Источник состава работ и DoD: [`docs/tasks/tasklist-database.md`](../../../../../../tasks/tasklist-database.md), блок 3.

## Цель

Зафиксировать в отдельном ADR практики работы с БД в репозитории (миграции, подмена драйвера для Alembic, соглашения, репозитории) без дублирования ADR-002; подготовить практическую справку [`docs/tech/db-tooling-guide.md`](../../../../../../tech/db-tooling-guide.md) с командами и путями; обновить реестр ADR.

## План работ

1. Добавить [`docs/adr/adr-004-db-tooling.md`](../../../../../../adr/adr-004-db-tooling.md): контекст, отсылка к ADR-002, соглашения по схеме, синхронный Alembic + psycopg2, ссылка на справку.
2. Создать [`docs/tech/db-tooling-guide.md`](../../../../../../tech/db-tooling-guide.md): `DATABASE_URL`, структура `backend/`, команды `make migrate-backend` / `alembic`, именование ревизий, примечание про задачу 04 (`db-*`).
3. Внести ADR-004 в [`docs/adr/README.md`](../../../../../../adr/README.md).
4. Исправить DoD блока 3 в `tasklist-database.md` (ссылки на `adr-001` → `adr-004` + ADR-002).
5. Самопроверка по обновлённому DoD.

## Критерии готовности (DoD)

См. блок 3 в [`tasklist-database.md`](../../../../../../tasks/tasklist-database.md).

## Связанные задачи

- **До:** задачи 01–02 (сценарии, `data-model.md`).
- **После:** задача 04 (Docker, make `db-*`, обновление справки при необходимости).
