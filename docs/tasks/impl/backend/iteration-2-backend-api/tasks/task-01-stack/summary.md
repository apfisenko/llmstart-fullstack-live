# Задача 01: Summary — Выбор backend-стека и фиксация решений

**Итерация:** 2 — Backend API  
**Статус:** Done  
**Дата:** 2026-04-06

---

## Что сделано

1. **Создан `plan.md` задачи** (`docs/tasks/impl/backend/iteration-2-backend-api/tasks/task-01-stack/plan.md`) — полная таблица стека, структура каталогов, согласование с `data-model.md`.

2. **Создан ADR-002** (`docs/adr/adr-002-backend-stack.md`) — зафиксировано решение по HTTP-слою и доступу к данным: FastAPI + uvicorn, SQLAlchemy 2.x async + asyncpg, Alembic, pydantic-settings; разобраны альтернативы (Django, sync SQLAlchemy, Tortoise ORM, сырой SQL).

3. **Обновлён `docs/adr/README.md`** — добавлена запись ADR-002 в реестр.

4. **Расширен `.cursor/rules/conventions.mdc`** — явные секции **Backend** и **Telegram-бот**:
   - Backend: FastAPI, pydantic-settings, SQLAlchemy async, asyncpg, Alembic, pytest + httpx, ruff, структура `backend/app/`; PostgreSQL как основная СУБД.
   - Бот: правила прежние; явно указано, что история в памяти — временное состояние до итерации 5.

5. **Обновлён `docs/vision.md` §9** — таблица технологий дополнена конкретными backend-инструментами (FastAPI, uvicorn, pydantic-settings, SQLAlchemy async, asyncpg, Alembic, pytest + httpx) и ссылкой на ADR-002.

---

## Отклонения от плана

Отклонений нет. README.md изменений не потребовал — команда запуска backend появится в задаче 06 при написании документации.

---

## Принятые решения

- **ADR-002 создан** (а не добавлен в §9 vision.md) — решение значимо и затрагивает несколько компонентов; самостоятельный ADR проще сослаться из задач 03–05.
- **`plan.md` итерации 2** (`docs/plan.md`) не менялся — DoD совместим с выбранным стеком без изменений.

---

## Ссылки

- [ADR-002](../../../../adr/adr-002-backend-stack.md)
- [ADR-001](../../../../adr/adr-001-database.md)
- [conventions.mdc](../../../../../.cursor/rules/conventions.mdc)
- [vision.md §9](../../../../vision.md)
- [plan.md задачи](plan.md)
