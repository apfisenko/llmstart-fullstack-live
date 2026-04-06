# Задача 01: Выбор backend-стека и фиксация решений

**Итерация:** 2 — Backend API  
**Статус:** In Progress  
**Дата:** 2026-04-06

---

## Цель

Зафиксировать стек backend-ядра (HTTP, конфиг, ORM, миграции), отразить выбор в ADR и правилах (`conventions.mdc`), привести проектную документацию в единое согласованное состояние без противоречий с ADR-001 и DoD итерации 2.

---

## Стек (принятые решения)

| Область | Выбор | Версия (ориентир) | Роль |
|---------|-------|-------------------|------|
| HTTP-фреймворк | **FastAPI** | 0.111+ | Маршруты, Pydantic-схемы, OpenAPI |
| ASGI-сервер | **uvicorn** | 0.29+ | Запуск приложения |
| Конфигурация | **pydantic-settings** | 2.x | Чтение `.env`, валидация, fail fast |
| СУБД | **PostgreSQL** | 15+ | Принято ADR-001 |
| Драйвер | **asyncpg** | 0.29+ | Асинхронный клиент PostgreSQL |
| ORM | **SQLAlchemy 2.x (async)** | 2.0+ | Модели, сессии; `AsyncSession` |
| Миграции | **Alembic** | 1.13+ | Версии схемы, `env.py` с async-движком |
| Тесты | **pytest** + **httpx** | latest | `AsyncClient` / `TestClient` для HTTP-слоя |
| Линт/формат | **ruff** | latest | Единый инструмент (вместо flake8 + black) |
| Зависимости | **uv** + `pyproject.toml` | latest | Как у бота; workspace/отдельный проект |
| Логирование | stdlib **logging** → stdout | — | Без текста переписки (см. conventions) |

---

## Структура каталогов (канонический вид для conventions)

```
backend/
├── app/
│   ├── main.py               # FastAPI app, lifespan, include_router
│   ├── config.py             # pydantic-settings Config, fail fast
│   ├── api/
│   │   ├── deps.py           # общие Depends (сессия БД, текущий пользователь)
│   │   └── v1/
│   │       ├── router.py     # APIRouter(prefix="/api/v1")
│   │       └── routes_*.py   # эндпоинты по доменам
│   ├── domain/               # Pydantic/SQLAlchemy-модели, правила домена
│   ├── infrastructure/       # сессия БД (async engine), LLM-клиент
│   └── services/             # сценарии между api и domain
├── migrations/               # Alembic
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py
│   └── test_*.py
├── pyproject.toml            # зависимости и настройки ruff/pytest
└── .env.example
```

---

## Согласование с data-model.md и ADR-001

- Движок PostgreSQL — принят, не переобсуждается.
- Доменные сущности из `data-model.md` (`User`, `Cohort`, `CohortMembership`, `Dialogue`, `DialogueMessage`, `Submission`) реализуются как SQLAlchemy-модели в `domain/` с UUID-ключами.
- Репозитории / фабрики сессий живут в `infrastructure/`, инжектируются через `deps.py`.
- Первое подключение Postgres и миграции — в рамках задач 03–05 итерации 2; расширение схемы под полную доменную модель — в итерации 3 по `tasklist-database.md`.

---

## Связь с ADR

- **ADR-001** — выбор PostgreSQL: принят, изменений нет.
- **ADR-002** — HTTP-слой и доступ к данным: создаётся в рамках этой задачи (`docs/adr/adr-002-backend-stack.md`).

---

## Definition of Done

- [x] Стек зафиксирован (этот документ + ADR-002)
- [x] `conventions.mdc` содержит раздел backend без противоречий с разделом бот
- [x] `vision.md` §9 совпадает с принятым стеком
- [x] `docs/adr/README.md` обновлён (ADR-002 в списке)
- [x] Нет противоречий: ядро — backend, LLM только из backend, конфиг через `.env`
