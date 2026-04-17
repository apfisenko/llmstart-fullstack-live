# Задача 06: документация backend

## Цель

Любой разработчик поднимает backend по инструкции: переменные окружения, запуск, OpenAPI, команды проверки. Согласованность [README.md](../../../../../../../README.md), [Makefile](../../../../../../../Makefile), [`backend/.env.example`](../../../../../../../backend/.env.example).

## Состав работ

- Обновить корневой `README.md`: быстрый старт backend (`uv`, `.env`), `/health`, `/docs`, `/openapi.json`, `/redoc`, PostgreSQL + `make migrate-backend`, SQLite по умолчанию, тесты (`make test-backend`), линт из `backend/` через `uv run ruff`; разделить команды бота и backend; убрать путаницу с продуктовой «итерацией 6».
- Сверить и при необходимости уточнить комментарии в `backend/.env.example` относительно `Settings` в `app/config.py`.
- Обновить `docs/integrations.md`: живая схема OpenAPI сейчас; кратко про секреты в env.
- Обновить `docs/plan.md`: итерация 2 — 🚧 In Progress до задачи 08; реализация и документация backend (05–06) завершены.
- Синхронизировать `backend/README.md` с корнем без дублирования.
- Обновить статус задачи в `docs/tasks/tasklist-backend.md`.

## Критерии готовности (DoD)

| # | Критерий |
|---|----------|
| 1 | С нуля: клон → копия `.env` → запуск → `health` и `/docs` доступны по шагам из README |
| 2 | Цели `Makefile` и текст README совпадают по именам команд |
| 3 | Нет скрытых шагов; OpenAPI явно указан (`/docs`, `/openapi.json`) |

## Связанные файлы

- [README.md](../../../../../../../README.md)
- [backend/README.md](../../../../../../../backend/README.md)
- [Makefile](../../../../../../../Makefile)
- [backend/.env.example](../../../../../../../backend/.env.example)
- [docs/integrations.md](../../../../../../integrations.md)
- [docs/plan.md](../../../../../../plan.md)
