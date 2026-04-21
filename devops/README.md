# DevOps: локальные образы и Compose

Единый манифест — корневой [`docker-compose.yml`](../docker-compose.yml). Отдельного compose «только БД» нет: сервис `postgres` без профиля; приложения (`backend`, `web`, `bot`) в профиле **`app`**.

## Структура

| Путь | Назначение |
|------|------------|
| [`devops/backend/Dockerfile`](backend/Dockerfile), [`docker-entrypoint.sh`](backend/docker-entrypoint.sh) | Backend: uv, Alembic при старте, uvicorn |
| [`devops/bot/Dockerfile`](bot/Dockerfile) | Telegram-бот из корневого `pyproject.toml` + `bot/` |
| [`devops/web/Dockerfile`](web/Dockerfile) | Next.js multi-stage, `output: "standalone"` |
| [`devops/postgres/docker-entrypoint-initdb.d/`](postgres/docker-entrypoint-initdb.d/) | Init SQL (например БД для pytest) |

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

## Образы в GHCR (CI)

Workflow: [`.github/workflows/ghcr.yml`](../.github/workflows/ghcr.yml) — на `push` в `main`/`master`, на `pull_request` (только **сборка**, без push) и `workflow_dispatch`.

Имена пакетов (всё в **нижнем регистре**):

| Сервис | Образ |
|--------|--------|
| backend | `ghcr.io/<OWNER>/<REPO>-backend` |
| web | `ghcr.io/<OWNER>/<REPO>-web` |
| bot | `ghcr.io/<OWNER>/<REPO>-bot` |

`<OWNER>` — `github.repository_owner`, `<REPO>` — имя репозитория без владельца (как в URL GitHub).

Теги при `push` в **`main`** или **`master`**: **`latest`** и **полный SHA** коммита на каждый образ. Точный откат: подставьте в `IMAGE_TAG` значение SHA из вкладки Packages / run workflow.

Локальный Compose **без** `docker build` приложений: файл [`docker-compose.ghcr.yml`](../docker-compose.ghcr.yml) подставляет `image:` поверх [`docker-compose.yml`](../docker-compose.yml). Переменные:

- **`GHCR_IMAGE_NAMESPACE`** — владелец (lower case), например `octocat`;
- **`GHCR_IMAGE_REPO`** — имя репо (lower case), например `llmstart-fullstack-live`;
- **`IMAGE_TAG`** — опционально, по умолчанию `latest` (или полный SHA образа из GHCR).

Команды: `make stack-pull-ghcr` и `make stack-up-ghcr`, либо `.\tasks.ps1 stack-pull-ghcr` / `stack-up-ghcr` (при Docker только в WSL — `stack-*-ghcr-wsl`). Подробнее: [`docs/tech/docker-compose-local.md`](../docs/tech/docker-compose-local.md).

Если пакеты **приватные**, перед `pull` выполните `docker login ghcr.io` (GitHub username + PAT с правом **`read:packages`**; для push из CI используется `GITHUB_TOKEN`).

### Compose «registry» и docker-expert

В смерженном конфиге у `backend`/`web`/`bot` остаётся и `build`, и `image`. Для запуска **только** из registry после `pull` используйте **`docker compose ... up --no-build`** (см. цели `stack-up-ghcr`): подтянутый тег из GHCR используется как образ контейнера, локальная сборка Dockerfile не выполняется.
