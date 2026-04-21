# LLMStart — веб-клиент

Next.js (App Router) в монорепозитории LLMStart: кабинет студента и преподавателя. Данные и правила — только в **backend**; здесь UI и route handlers, которые проксируют запросы к API по `BACKEND_ORIGIN`.

## Требования

- **Node.js 22** и **pnpm 10** (как в [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml))
- Запущенный backend (и Postgres для сценариев с БД)

## Окружение

1. Скопируйте [`.env.example`](.env.example) → **`.env.local`**.
2. Задайте **`BACKEND_ORIGIN`** (например `http://127.0.0.1:8000`, без завершающего `/`).
3. Если в `backend/.env` включён **`BACKEND_API_CLIENT_TOKEN`**, продублируйте его в **`.env.local`**.

## Команды

Из **корня** репозитория (рекомендуется):

```bash
make frontend-install
make frontend-dev
```

или в PowerShell: `.\tasks.ps1 frontend-install`, `.\tasks.ps1 frontend-dev`.

Из каталога `frontend/web/`:

```bash
pnpm install
pnpm dev
```

Проверки качества (как часть CI): **`pnpm lint`**, **`pnpm build`**. Отдельного **`pnpm test`** в проекте нет.

Сборка статики вместе с backend-линтом из корня: **`make ci-check`** / **`.\tasks.ps1 ci-check`** (после `make install` и `make frontend-install`).

## Smoke после БД

1. Из корня: **`make db-up`** (или `.\tasks.ps1 db-up`).
2. Запустите backend (см. [backend/README.md](../../backend/README.md)).
3. `pnpm dev` → откройте **`/login`**, при необходимости сценарий dev-session — в корневом [README.md](../../README.md).

## Документация

- [Онбординг](../../docs/onboarding.md)
- [Архитектура](../../docs/architecture.md)
- [Контракты API](../../docs/tech/api-contracts.md)
- Корневой [README.md](../../README.md)
