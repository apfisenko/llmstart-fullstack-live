# Итерация 4: реализация frontend

## Цель

Единый веб-клиент с ролями студента и преподавателя: вызовы только в HTTP API ядра (`/api/v1/`), без дублирования бизнес-логики ([`docs/vision.md`](../../../../vision.md)).

## Ценность

Студент и преподаватель работают с потоком через браузер; UI согласован с [`docs/ui/ui-requirements.md`](../../../../ui/ui-requirements.md) и макетами в [`docs/tasks/tasklist-frontend.md`](../../../../tasks/tasklist-frontend.md) (#ui-mockups).

## Задачи (последовательность)

| # | Задача | План |
|---|--------|------|
| 01 | Требования к UI (зоны A–D), стиль, вход по Telegram username, контракты API | [task-01](tasks/task-01-ui-api-contracts/plan.md) |
| 02 | Backend: данные, эндпоинты, миграции, mock, преподаватель | [task-02](tasks/task-02-backend-api-seed/plan.md) |
| 03 | Каркас Next.js, вход, layout, чат-каркас, Makefile, бот `/username` | [task-03](tasks/task-03-next-scaffold/plan.md) |
| 04–08 | См. [`docs/tasks/tasklist-frontend.md`](../../../../tasks/tasklist-frontend.md) | — |
| 11 | Кабинет студента (зона C): экран прогресса и сдачи — **✅** | [task-11](tasks/task-11-student-cabinet/plan.md) \| [summary](tasks/task-11-student-cabinet/summary.md) |

## Источники контекста

- [`docs/plan.md`](../../../../plan.md) — §«Итерация 4»
- [`docs/tasks/tasklist-frontend.md`](../../../../tasks/tasklist-frontend.md)
- [`docs/data-model.md`](../../../../data-model.md), [`docs/tech/api-contracts.md`](../../../../tech/api-contracts.md)

## Артефакты итерации

`frontend/web/` (после задачи 03), обновлённые контракты в `docs/api/openapi-v1.yaml` и `docs/tech/api-contracts.md`. Итоговый `summary.md` итерации — после закрытия всех задач итерации.
