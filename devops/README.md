# DevOps: локальные образы и Compose

Единый манифест — корневой [`docker-compose.yml`](../docker-compose.yml). Отдельного compose «только БД» нет: сервис `postgres` без профиля; приложения (`backend`, `web`, `bot`) в профиле **`app`**.

## Структура

| Путь | Назначение |
|------|------------|
| [`devops/backend/Dockerfile`](backend/Dockerfile), [`docker-entrypoint.sh`](backend/docker-entrypoint.sh) | Backend: uv, Alembic при старте, uvicorn |
| [`devops/bot/Dockerfile`](bot/Dockerfile) | Telegram-бот из корневого `pyproject.toml` + `bot/` |
| [`devops/web/Dockerfile`](web/Dockerfile) | Next.js multi-stage, `output: "standalone"` |
| [`devops/postgres/docker-entrypoint-initdb.d/`](postgres/docker-entrypoint-initdb.d/) | Init SQL (например БД для pytest) |
| [`devops/vps/`](vps/README.md) | Подготовка VPS: bootstrap Docker + Compose (Debian/Ubuntu), см. [docs/tech/vps-manual-ghcr-deploy.md](../docs/tech/vps-manual-ghcr-deploy.md) |

Сборка **всегда с контекстом корня репозитория** (чтобы подтянуть `backend/`, `bot/`, `frontend/web/` и общий [`.dockerignore`](../.dockerignore)):

```bash
docker build -f devops/backend/Dockerfile .
docker build -f devops/bot/Dockerfile .
docker build -f devops/web/Dockerfile .
```

## Compose

- Только PostgreSQL: `docker compose up -d postgres` (или `make db-up` / `.\tasks.ps1 db-up` — миграции с хоста).
- Полный стек: `docker compose --profile app up -d --wait` (`make stack-up` / `.\tasks.ps1 stack-up`).
- Перед `stack-up` нужны **`backend/.env`** и **`bot/.env`** (см. `*.env.example`). `DATABASE_URL` для контейнера backend задаётся в compose и перекрывает значение из файла, чтобы использовать хост `postgres`.

## Docker review notes (docker-expert)

- **Multi-stage** для `web`: зависимости и сборка отделены от runtime-образа.
- **Пинning** базовых образов: `python:3.12.8-slim-bookworm`, `node:22.14-bookworm-slim`, `postgres:16-alpine`, образ `uv` с фиксированным тегом.
- **`.dockerignore` в корне**: меньше контекст, без `.env` и артефактов.
- **Non-root**: `appuser` (backend), `botuser` (bot), `nextjs` (web).
- **HEALTHCHECK** на `postgres`, `backend`, `web`, `bot`; в compose для приложений — `depends_on` с `condition: service_healthy` где нужен порядок старта.
- **Секреты** не копируются в образы; токены и ключи — через `env_file` / переменные окружения на этапе `compose up`.
- **Именованный том** `llmstart_pg_data` для данных Postgres.
- **Init SQL** в одном месте: `devops/postgres/` (каталог `docker/postgres/` — только [README-редирект](../docker/postgres/README.md)).

## GHCR (образы из CI)

После **успешного CI** на **`main`** или **`master`** (или при ручном запуске) workflow [`.github/workflows/ghcr.yml`](../.github/workflows/ghcr.yml) собирает три образа и пушит в **GitHub Container Registry**.

### Имена и теги

Корень (владелец и репозиторий GitHub в **нижнем регистре**):

`ghcr.io/<owner>/<repo>`

Образы (отдельные пакеты в GHCR):

| Сервис  | `image` (без тега) |
|---------|---------------------|
| backend | `ghcr.io/<owner>/<repo>/backend` |
| web     | `ghcr.io/<owner>/<repo>/web` |
| bot     | `ghcr.io/<owner>/<repo>/bot` |

Теги на каждый успешный прогон: **`latest`** и **`sha-<short>`** (первые 7 символов коммита). Для фиксированной версии укажите `IMAGE_TAG=sha-abcdef1` в окружении или в `.env` рядом с compose.

### Локальный стек без `docker build` приложений

Файл **[`docker-compose.ghcr.yml`](../docker-compose.ghcr.yml)** — тот же стек, что в корневом compose, но вместо `build` указаны `image` из GHCR. Переменная **`LLMSTART_GHCR_IMAGE_ROOT`** должна совпадать с корнем образов (например `ghcr.io/myorg/llmstart-fullstack-live`). Пример значений — [`.env.ghcr.example`](../.env.ghcr.example).

```bash
# в .env или export:
export LLMSTART_GHCR_IMAGE_ROOT=ghcr.io/myorg/llmstart-fullstack-live
export IMAGE_TAG=latest

docker compose -f docker-compose.ghcr.yml --profile app up -d --wait
```

Удобные цели: **`make stack-up-ghcr`** / **`make stack-down-ghcr`**, **`.\tasks.ps1 stack-up-ghcr`** или **`stack-up-ghcr-wsl`** (Docker только в WSL).

Подробности (логин в GHCR при приватных пакетах, WSL): **[`docs/tech/docker-compose-ghcr.md`](../docs/tech/docker-compose-ghcr.md)**.

### Compose «из registry» vs локальный build

Сервисы, порты, `depends_on`, healthcheck и env совпадают с [корневым `docker-compose.yml`](../docker-compose.yml); отличается только источник образов (`image` вместо `build`). Postgres по-прежнему официальный `postgres:16-alpine` из Docker Hub.

**Ревью (docker-expert):** отдельный YAML вместо merge-override исключает конфликт «одновременно `build` и `image`» в Compose; дублирование манифеста осознанно минимально и синхронизируется с основным compose при изменении сервисов.
