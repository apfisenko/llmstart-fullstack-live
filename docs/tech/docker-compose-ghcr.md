# Стек из образов GHCR

Публикация образов выполняется workflow [`.github/workflows/ghcr.yml`](../../.github/workflows/ghcr.yml) после **успешного** завершения workflow **CI** на **`main`** или **`master`** (и вручную через **Actions → GHCR images → Run workflow**).

## Имена образов

Шаблон (нижний регистр для `owner` и `repo`):

- `ghcr.io/<owner>/<repo>/backend:<tag>`
- `ghcr.io/<owner>/<repo>/web:<tag>`
- `ghcr.io/<owner>/<repo>/bot:<tag>`

Теги: **`latest`** и **`sha-<short>`** (короткий SHA коммита).

В [корневом `docker-compose.ghcr.yml`](../../docker-compose.ghcr.yml) используется префикс без имени сервиса:

```text
${LLMSTART_GHCR_IMAGE_ROOT}/backend:${IMAGE_TAG:-latest}
```

Задайте, например:

```bash
export LLMSTART_GHCR_IMAGE_ROOT=ghcr.io/mygithubuser/llmstart-fullstack-live
export IMAGE_TAG=latest
```

Либо добавьте те же переменные в **корневой `.env`** (файл в `.gitignore`) — Compose подставит их при интерполяции. Шаблон без секретов: [`.env.ghcr.example`](../../.env.ghcr.example).

## Логин в GHCR (`docker pull` / compose up)

Если пакеты **публичные**, логин не нужен.

Если пакеты **приватные** (настройки visibility в GitHub → Packages):

```bash
echo "<GITHUB_TOKEN>" | docker login ghcr.io -u <GITHUB_USERNAME> --password-stdin
```

Токен с правом **`read:packages`** (классический PAT) или fine-grained с доступом к репозиторию и чтению пакетов. Для одноразового pull можно использовать [PAT из настроек разработчика](https://github.com/settings/tokens).

## Запуск compose

Из корня репозитория (нужны по-прежнему `backend/.env`, `bot/.env`, см. [docker-compose-local.md](docker-compose-local.md)):

```bash
make stack-up-ghcr
make stack-down-ghcr
```

**Docker через WSL (Windows):** если в PowerShell нет `docker` в PATH, используйте терминал WSL или цели **`make stack-up-ghcr`** с `DOCKER_COMPOSE="wsl -e docker compose"` (как в [Makefile](../../Makefile) для `db-up`), либо **`.\tasks.ps1 stack-up-ghcr-wsl`** — тот же механизм `--project-directory` в `/mnt/...`, что у `stack-up-wsl`. Скрипт читает **`LLMSTART_GHCR_IMAGE_ROOT`** (и при необходимости **`IMAGE_TAG`**, **`BACKEND_API_CLIENT_TOKEN`**) из корневого **`.env`** или из **`$env:`** в PowerShell и передаёт их в `wsl` через `env`, потому что переменные сессии PowerShell сами в WSL не попадают.

Проверки **`check-backend`** / **`check-web`** на localhost те же; **`check-bot`** выполняйте после подъёма стека, когда в PATH доступен `docker compose` к тому же проекту (или `docker exec` в контейнер `llmstart-bot`).

## Связь с локальным compose

Локальная сборка из Dockerfile: [docker-compose-local.md](docker-compose-local.md) и корневой [`docker-compose.yml`](../../docker-compose.yml). Сценарий GHCR не заменяет его — это отдельный файл с теми же сервисами и образами из registry.

## VPS / прод (ручной шаг `docker login`)

На сервере используются **те же** переменные (`.env` рядом с compose, `LLMSTART_GHCR_IMAGE_ROOT`, при необходимости `BACKEND_API_CLIENT_TOKEN` и `backend/.env` / `bot/.env`), что и при локальном [§ «Запуск compose»](#запуск-compose) выше.

**`docker login ghcr.io` на сервере** выполняет **только** владелец (PAT / fine-grained, `read:packages` для приватных пакетов) — **не** автоматизируется агентом. Готовые команды и порядок: [vps-manual-ghcr-deploy.md](vps-manual-ghcr-deploy.md). Для **публичных** пакетов в GHCR логин **не** нужен.

**Связка с облаком:** [timeweb-vps.md](timeweb-vps.md) (VPS, SSH, `twc`), чеклист — [итерация 4 в tasklist-devops.md](../tasks/tasklist-devops.md#iteration-4-server-setup).
