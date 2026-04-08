# Итерация: слой данных (PostgreSQL)

## Цель

Заменить временное in-memory хранение в backend на персистентный слой PostgreSQL, сохранив и уточнив пользовательские сценарии, схему данных, инструменты (Alembic, make) и сквозную работу API.

## Ценность

Единый источник истины по пользователям, потоку, прогрессу и диалогам; основа для бота и веб-клиентов без смены HTTP-контракта.

## Задачи (последовательность)

| # | Задача | Ссылка на план |
|---|--------|----------------|
| 01 | Сценарии студент/преподаватель и требования к данным | [task-01](tasks/task-01-scenarios-data-reqs/plan.md) |
| 02 | Схема: логика + физика, ER, ревью | [task-02](tasks/task-02-schema-er-review/plan.md) |
| 03 | ADR по БД-инструментам + справка workflow | [task-03](tasks/task-03-adr-db-tooling-guide/plan.md) |
| 04 | Docker Postgres, миграции, сид | [task-04](tasks/task-04-infra-seed-import/plan.md) |
| 05 | ORM, репозитории, интеграция backend | [task-05](tasks/task-05-orm-repos-pg/plan.md) |

## Источники контекста

- Продукт: [`docs/idea.md`](../../../../idea.md), [`docs/vision.md`](../../../../vision.md)
- Контракт API: [`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md), [`docs/data-model.md`](../../../../data-model.md)
- Сводная декомпозиция: [`docs/tasks/tasklist-database.md`](../../../../tasks/tasklist-database.md)

## Артефакты итерации (целевые)

См. `tasklist-database.md` по блокам 1–5; итоговый `summary.md` итерации — после завершения всех задач.
