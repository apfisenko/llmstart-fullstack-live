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

## CD: автодеплой (GitHub Actions)

После того как job **build-push** в [`.github/workflows/ghcr.yml`](../../.github/workflows/ghcr.yml) опубликует все три образа (backend, bot, web), job **deploy** по SSH на VPS выполняет в каталоге деплоя: `git fetch` → `git checkout` на **тот же commit SHA**, что и сборка, затем при необходимости `docker login` к GHCR, `docker compose -f docker-compose.ghcr.yml --profile app pull` и `up -d --wait` с `IMAGE_TAG=latest` (образы `latest` только что ушли в registry в этом же run).

**Цепочка:** push в `main` / `master` → **CI** (успех) → **GHCR images** (сборка и push) → **Deploy to VPS**. Ручной запуск **Actions → GHCR images → Run workflow** тоже прогоняет публикацию и деплой (разумная проверка CD).

| Secret | Назначение | Как workflow использует |
|--------|------------|------------------------|
| `DEPLOY_HOST` | Хост или IP VPS | SSH: поле `host` |
| `DEPLOY_USER` | Пользователь Linux на сервере | SSH: `username` |
| `SSH_PRIVATE_KEY` | Приватный SSH-ключ **только для CI/CD** (многострочный PEM, целиком от `-----BEGIN` до `-----END…`) | В CI пишется в файл, SSH по `key_path` |
| `DEPLOY_SSH_KNOWN_HOSTS` | Содержимое `known_hosts` для хоста (см. `ssh-keyscan -H` на своей машине) | **Рекомендуется:** пиннинг ключа. Если **не** задан, в CI выполняется **`ssh-keyscan`** к `DEPLOY_HOST` (хост с runner GitHub должен быть доступен по сети; при смене ключа на сервере перезапустите деплой или обновите секрет) |
| `DEPLOY_SSH_PORT` | Порт SSH, если не **22** | Необязательно: если пусто, используется `22` |
| `DEPLOY_PATH` | Абсолютный путь к **корню** `git clone` на сервере: каталог, где лежат **`.git`**, `docker-compose.ghcr.yml` (напр. `/opt/llmstart`, см. [vps-manual-ghcr-deploy.md](vps-manual-ghcr-deploy.md#2-копирование-репозитория-на-vps)) | `cd` и `git fetch` / `checkout`. Если пусто или путь не клона — `fatal: not a git repository` |
| `GHCR_DEPLOY_READ_TOKEN` | Токен с **`read:packages`** (PAT / fine-grained) | Необязательно: если задан, на VPS выполняется `echo … \| docker login ghcr.io -u <user> --password-stdin` перед `compose pull` (**приватные** пакеты GHCR). Значения **не** печатать в логах. |
| `GHCR_DEPLOY_READ_USER` | GitHub-**аккаунт владельца** токена (логин для `docker login`) | Необязательно: если пусто, подставляется `github.repository_owner` (подходит, если PAT выдан тому же пользователю/боту) |

Секреты создаёт **владелец** репозитория: **Settings → Secrets and variables → Actions**; в документации и в issues **не** дублировать значения.

**Согласованность ref:** в `.env` на сервере при CD достаточно `IMAGE_TAG=latest`; checkout по полному SHA держит на сервере **те же** `docker-compose.ghcr.yml` и пути, что в коммите образов. Для `git fetch` / `git checkout` на сервере должен быть настроен доступ к репозиторию (как в [vps-manual-ghcr-deploy.md](vps-manual-ghcr-deploy.md#2-копирование-репозитория-на-vps) — deploy key или HTTPS + PAT клон).

---

## VPS / прод: ручной `docker login` (вне GHA)

На сервере используются **те же** переменные (`.env` рядом с compose, `LLMSTART_GHCR_IMAGE_ROOT`, при необходимости `BACKEND_API_CLIENT_TOKEN` и `backend/.env` / `bot/.env`), что и при локальном [§ «Запуск compose»](#запуск-compose) выше.

**Ручной** сценарий: **`docker login ghcr.io` на сервере** (PAT, `read:packages` для приватных пакетов) — ввод **владелец** на машине, без публикации токена в репо; готовые команды: [vps-manual-ghcr-deploy.md](vps-manual-ghcr-deploy.md). Автодеплой из GitHub для приватных пакетов использует секрет **`GHCR_DEPLOY_READ_TOKEN`**, см. [§ CD](#cd-автодеплой-github-actions). Для **публичных** пакетов логин на сервере **не** нужен.

**Связка с облаком:** [timeweb-vps.md](timeweb-vps.md) (VPS, SSH, `twc`), чеклист — [итерация 4 в tasklist-devops.md](../tasks/tasklist-devops.md#iteration-4-server-setup).
