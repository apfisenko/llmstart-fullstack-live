# Задача 03: Summary — Каркас backend-сервиса

**Итерация:** 2 — Backend API  
**Статус:** Done  
**Дата:** 2026-04-06

---

## Что сделано

1. Создан каталог [`backend/`](../../../../../../../backend/) с [`pyproject.toml`](../../../../../../../backend/pyproject.toml), пакетом [`app/`](../../../../../../../backend/app/), пустыми [`migrations/`](../../../../../../../backend/migrations/) (placeholder под Alembic).
2. Реализованы [`app/main.py`](../../../../../../../backend/app/main.py) (lifespan, `GET /health`, подключение v1), [`app/config.py`](../../../../../../../backend/app/config.py) (pydantic-settings), [`app/api/deps.py`](../../../../../../../backend/app/api/deps.py) (`SettingsDep`), [`app/api/v1/router.py`](../../../../../../../backend/app/api/v1/router.py) — пустой префикс `/api/v1`.
3. Настроен [`ruff`](../../../../../../../backend/pyproject.toml) в `pyproject.toml`; проверка: `uv run ruff check app`.
4. Обновлён [`backend/.env.example`](../../../../../../../backend/.env.example); кратко — корневой [`README.md`](../../../../../../../README.md) и [`backend/README.md`](../../../../../../../backend/README.md).

---

## Отклонения от черновика плана

- Отдельный [`backend/README.md`](../../../../../../../backend/README.md) добавлен как `readme` проекта в `pyproject.toml` (удобство `uv`/пакета).
- Хост/порт процесса задаются аргументами `uvicorn` в README; переменные `BACKEND_HOST`/`BACKEND_PORT` в `Settings` зарезервированы для следующих задач (CLI-обёртка не вводилась).
- Обязательный `BACKEND_API_CLIENT_TOKEN` из черновика плана **убран**: в каркасе нет проверки `Authorization: Bearer`, поле только мешало старту. Секрет для клиентов API введётся вместе с реализацией защищённых маршрутов (задача 05+), см. [`integrations.md`](../../../../../../integrations.md).

---

## Переменные окружения (каркас)

| Переменная | Обязательность | Назначение |
|------------|----------------|------------|
| `BACKEND_HOST` | Нет (default `127.0.0.1`) | Зарезервировано |
| `BACKEND_PORT` | Нет (default `8000`) | Зарезервировано |
| `LOG_LEVEL` | Нет (default `INFO`) | Уровень логирования |

---

## Ссылки

- [План задачи](plan.md)
- [ADR-002](../../../../../../adr/adr-002-backend-stack.md)
