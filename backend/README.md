# LLMStart — backend

HTTP API ядра: FastAPI, конфиг из **`backend/.env`** (все переменные процесса backend, включая **`DATABASE_URL`**). Краткий сценарий «с нуля» — в корневом [README.md](../README.md); здесь — детали.

Запуск из каталога `backend/` (хост/порт должны совпадать с `BACKEND_HOST` / `BACKEND_PORT` в `.env`):

```bash
uv sync
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### `uv sync`: «Отказано в доступе» / `failed to persist ... uvicorn.exe` (Windows)

Чаще всего **запущен backend** (или другой процесс), который использует `backend\.venv\Scripts\uvicorn.exe` или `python.exe` из этого venv — файл занят, установка не может его заменить.

1. Остановите сервер (**Ctrl+C** в терминале с uvicorn) или закройте IDE-запуск.
2. При необходимости в PowerShell: `Get-Process uvicorn, python | Where-Object { $_.Path -like '*backend\.venv*' }` — завершите лишние процессы (`Stop-Process -Id <pid> -Force`).
3. Повторите **`uv sync`**.

Если ошибка остаётся — временно отключите сканирование папки `.venv` в антивирусе или удалите каталог **`backend/.venv`** и выполните **`uv sync`** заново.

**База данных:** только **PostgreSQL**. В **`backend/.env`** обязательна строка **`DATABASE_URL`** (`postgresql+asyncpg://...`). Миграции: **`make migrate-backend`** из корня репо или `cd backend && uv run alembic upgrade head` (нужен `uv sync --extra dev` для `psycopg2`).

Переменные — см. [`backend/.env.example`](.env.example). Опционально `BACKEND_API_CLIENT_TOKEN`: если задан, для `/api/v1/*` нужен заголовок `Authorization: Bearer <токен>`. Для реального LLM: **`OPENROUTER_API_KEY`** и блок `OPENROUTER_*`, `SYSTEM_PROMPT_PATH`, при необходимости `PROXY_URL`.

Служебные маршруты: `GET /health`, `GET /health/db`. Документация OpenAPI: **`/docs`** (Swagger), **`/openapi.json`**, **`/redoc`**. Публичный API v1: префикс `/api/v1/` — см. [`docs/tech/api-contracts.md`](../docs/tech/api-contracts.md).

## Тесты

Интеграционные API-тесты — **`tests/pg/`** против PostgreSQL (отдельная БД `*_test`).

| Команда из корня репо | Из каталога `backend/` |
|-----------------------|-------------------------|
| `make test-backend` | `uv run pytest tests/pg` + **`TEST_DATABASE_URL`** на `…/llmstart_test` |

Общие фикстуры — [`tests/api_fixtures.py`](tests/api_fixtures.py), подключаются из [`tests/conftest.py`](tests/conftest.py). Перед каждым тестом схема из ORM пересоздаётся (`drop_all` / `create_all`).

**PostgreSQL:** `make db-up` поднимает контейнер и накатывает миграции на **`llmstart`** и **`llmstart_test`**. Затем `make test-backend`. **`make db-migrate-test`** — то же, что полный цикл миграций на обе БД, плюс **`tests/pg`**.

По умолчанию `uv run pytest` (без пути) смотрит в **`tests/pg`** — см. [`pyproject.toml`](pyproject.toml).
