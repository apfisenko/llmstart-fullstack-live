# Задача 03: Каркас backend-сервиса

**Итерация:** 2 — Backend API  
**Статус:** Done  
**Дата:** 2026-04-06

---

## Цель

Рабочий каркас `backend/`: `pyproject.toml` + `uv`, структура `app/` по [`.cursor/rules/conventions.mdc`](../../../../../../../.cursor/rules/conventions.mdc), конфигурация (fail-fast), `GET /health` вне `/api/v1/`, пустой роутер v1, `ruff`, обновление [`backend/.env.example`](../../../../../../../backend/.env.example) и [README](../../../../../../../README.md).

---

## Состав работ (факт)

| Шаг | Содержание |
|-----|------------|
| Структура | `backend/app/main.py`, `config.py`, `api/deps.py`, `api/v1/router.py`, `domain/`, `infrastructure/`, `services/`, `migrations/` (пусто, `.gitkeep`) |
| Зависимости | `backend/pyproject.toml`: FastAPI, uvicorn, pydantic-settings, python-dotenv; dev: ruff; сборка: hatchling |
| Конфиг | `Settings`: `BACKEND_HOST`, `BACKEND_PORT`, `LOG_LEVEL`; `env_file`: `.env`, `../.env` |
| Маршруты | `GET /health` → `{"status":"ok"}`; подключён `APIRouter(prefix="/api/v1")` без бизнес-маршрутов; `/docs`, `/openapi.json` — стандарт FastAPI |
| Документация | [backend/README.md](../../../../../../../backend/README.md); корневой README и `backend/.env.example` — секция backend |

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `uv sync` и `ruff check app` проходят | `cd backend && uv sync --extra dev && uv run ruff check app` |
| 2 | `GET /health` возвращает `{"status":"ok"}` | Запуск `uvicorn` по разделу «Команды проверки» ниже; `curl http://127.0.0.1:8000/health` |
| 3 | Каркас стартует без обязательных backend-only секретов; при добавлении обязательных полей в `Settings` — по-прежнему fail-fast (pydantic) | Запуск `uvicorn` с пустым/отсутствующим `.env` для переменных с дефолтами в `Settings` |

Те же проверки может выполнить пользователь для самостоятельной верификации.

---

## Вне scope (следующие задачи)

- PostgreSQL, Alembic с версиями, LLM, эндпоинты по [OpenAPI](../../../../../../../api/openapi-v1.yaml) — задачи 05+.
- `pytest` — задача 04.
- `Makefile` — при необходимости задача 08.

---

## Команды проверки

```bash
cd backend
uv sync --extra dev
uv run ruff check app
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
# curl http://127.0.0.1:8000/health
```

---

## Ссылки

- [tasklist-backend.md](../../../../../../tasklist-backend.md) — задача 03
- [docs/tech/api-contracts.md](../../../../../../tech/api-contracts.md) — health вне v1
