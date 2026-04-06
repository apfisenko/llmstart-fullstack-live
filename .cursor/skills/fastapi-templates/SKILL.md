---
name: fastapi-templates
description: >-
  Шаблоны структуры приложения FastAPI: приложение, роутеры, зависимости,
  настройки, lifespan. Используй при создании или расширении backend-сервиса,
  добавлении модулей API и настройке DI в проекте на FastAPI.
---

# Шаблоны FastAPI

## Структура каталогов (ориентир)

```
backend/
  main.py              # создание app, подключение роутеров
  config.py            # Pydantic Settings из env
  api/
    deps.py            # общие Depends (сессия БД, текущий пользователь)
    v1/
      router.py        # APIRouter(prefix="/api/v1")
      routes_*.py      # эндпоинты по доменам
  services/            # бизнес-логика, без привязки к HTTP
```

## Минимальный `main.py`

- `FastAPI(title=..., lifespan=lifespan)` при необходимости startup/shutdown.
- `app.include_router(api_v1_router)`.
- CORS и middleware — только если нужны; не включать «на всякий случай».

## Роутер

- Один `APIRouter` на область: `prefix="/flows"`, `tags=["flows"]`.
- Хендлеры тонкие: парсинг → вызов сервиса → маппинг в response model.
- Pydantic-модели для тела и ответа; не использовать `dict` в публичном контракте без причины.

## Настройки

- `pydantic-settings`: чтение из `.env`; обязательные поля без дефолтов — падать при старте с ясным сообщением (как в `bot/config.py`).

## Зависимости

- Общие вещи (БД, HTTP-клиент LLM) — в `deps.py`, провайдеры через `Depends`.
- Не прятать бизнес-логику внутри Depends; там только ввод/разрешение зависимостей.

## Тестируемость

- Сервисы с чистыми функциями/классами, принимающими порты (репозиторий, клиент) — удобнее мокать в тестах.
- Для HTTP-слоя — `TestClient` или `httpx.AsyncClient` с `ASGITransport` (см. skill `python-testing-patterns`).
