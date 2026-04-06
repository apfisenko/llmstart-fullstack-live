# LLMStart — backend

HTTP API ядра: FastAPI, конфиг из `.env`. Запуск из каталога `backend/`:

```bash
uv sync
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Переменные окружения — см. корневой `.env.example` (секция backend) и `backend/.env.example`. Для старта каркаса и `GET /health` достаточно обычного `.env` (например только с переменными бота); `BACKEND_API_CLIENT_TOKEN` обязателен, когда появятся защищённые маршруты (`Authorization: Bearer`).

Служебные маршруты: `GET /health`, документация OpenAPI: `/docs`, `/openapi.json`. Публичный API v1: префикс `/api/v1/` (реализация — следующие задачи).
