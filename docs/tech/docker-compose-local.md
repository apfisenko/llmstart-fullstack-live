# Локальный Docker Compose

Корневой [`docker-compose.yml`](../../docker-compose.yml) и каталог [`devops/`](../../devops/README.md). Один файл: сервис **`postgres`** без профиля; **backend**, **web**, **bot** — в профиле **`app`**.

**Docker через WSL (Windows):** если в PowerShell команда `docker` не находится, откройте терминал WSL (Ubuntu и т.п.), перейдите в каталог репозитория и запускайте `docker compose` / `docker build` там — так обычно подключён Docker Desktop (интеграция с WSL2).

**Образы из GHCR без локальной сборки приложений:** [`docker-compose-ghcr.md`](docker-compose-ghcr.md) и корневой [`docker-compose.ghcr.yml`](../../docker-compose.ghcr.yml); цели `stack-up-ghcr` / `stack-up-ghcr-wsl` в Makefile и `tasks.ps1`.

## Переменные и файлы окружения

| Файл | Назначение |
|------|------------|
| [`backend/.env`](../../backend/.env) | Обязателен для `stack-up`: ключи LLM, опционально `BACKEND_API_CLIENT_TOKEN` и т.д. (шаблон — [`backend/.env.example`](../../backend/.env.example)). В compose для контейнера backend поле **`DATABASE_URL` задаётся поверх** файла и указывает на хост `postgres`. |
| [`bot/.env`](../../bot/.env) | Обязателен для контейнера бота: `TELEGRAM_TOKEN`, при необходимости `COHORT_ID` / `MEMBERSHIP_ID`. Compose выставляет `BACKEND_HOST=backend` и **обнуляет `PROXY_URL` / `BACKEND_HTTP_PROXY`**, чтобы прокси с `127.0.0.1` хоста не ломали контейнер. Шаблон — [`bot/.env.example`](../../bot/.env.example). |
| Корневой `.env` рядом с compose | Опционально: **`BACKEND_API_CLIENT_TOKEN`** для сервиса `web` (тот же токен, что в `backend/.env`, если включена защита API). Подставляется в `docker-compose.yml` как `${BACKEND_API_CLIENT_TOKEN:-}`. |

Секреты не коммитить; в образы они не копируются.

## Только PostgreSQL

Поднять БД и накатить миграции с **хоста** (uv/Alembic на вашей машине):

```bash
make db-up
# Windows PowerShell:
# .\tasks.ps1 db-up
```

Эквивалент вручную:

```bash
docker compose up -d --wait postgres
# затем make db-migrate-all  или  .\tasks.ps1 db-migrate-all
```

Остановка:

```bash
make db-down
```

## Полный стек (backend + web + bot + postgres)

1. Подготовьте **`backend/.env`** и **`bot/.env`** (см. выше).
2. При использовании Bearer-токена для API задайте в окружении хоста перед `up` переменную **`BACKEND_API_CLIENT_TOKEN`** (и в `backend/.env`, и при необходимости в корневом `.env` для подстановки в web).

Сборка и запуск:

```bash
make stack-build   # при первом запуске или после смены Dockerfile
make stack-up
```

Windows PowerShell:

```powershell
.\tasks.ps1 stack-build
.\tasks.ps1 stack-up
```

Если `docker` доступен только из WSL:

```powershell
.\tasks.ps1 stack-up-wsl
```

Остановка приложений (postgres можно оставить или остановить отдельно):

```powershell
.\tasks.ps1 stack-down
```

Миграции в контейнере **backend** выполняются при старте (entrypoint: `alembic upgrade head`, затем uvicorn). Отдельный `make db-migrate` после `stack-up` обычно не нужен, если том БД уже с актуальной схемой.

## Диагностика

| Действие | Make | tasks.ps1 |
|----------|------|-----------|
| Статус контейнеров | `make stack-status` | `.\tasks.ps1 stack-status` |
| Логи (все сервисы профиля app) | `make stack-logs` | `.\tasks.ps1 stack-logs` |
| Логи одного сервиса | `make stack-logs STACK_SERVICE=web` | `$env:STACK_SERVICE='web'; .\tasks.ps1 stack-logs` |

## Проверка работоспособности

Сервисы должны слушать порты на localhost: **8000** (backend), **3000** (web).

| Компонент | Команда | Ожидаемый результат |
|-----------|---------|---------------------|
| Backend | `make check-backend` или `.\tasks.ps1 check-backend` | HTTP 200, тело ответа `/health`. |
| Web | `make check-web` или `.\tasks.ps1 check-web` | HTTP 2xx/3xx главной страницы. |
| Bot | `make check-bot` или `.\tasks.ps1 check-bot` | Из **запущенного** контейнера `bot`: успешный HTTP-запрос к `http://backend:8000/health` (без реального round-trip в Telegram). |

Проверка OpenAPI вручную: `curl -s http://127.0.0.1:8000/openapi.json | head`.

## Полезные команды

```bash
docker compose config
docker compose --profile app ps -a
```

Init SQL для тестовой БД: [`devops/postgres/docker-entrypoint-initdb.d/`](../../devops/postgres/docker-entrypoint-initdb.d/) (выполняется только при **первом** создании тома данных Postgres).

## Если контейнер `bot` постоянно в `Restarting`

Чаще всего:

1. **`ProxyConnectionError` к `127.0.0.1:…`** — в `bot/.env` задан `PROXY_URL` под прокси **на хосте**; внутри контейнера `127.0.0.1` — это не Windows. В [`docker-compose.yml`](../../docker-compose.yml) для сервиса `bot` **`PROXY_URL` и `BACKEND_HTTP_PROXY` принудительно пустые** (compose перекрывает `env_file`). Для прокси с хоста в Docker Desktop можно задать вручную override, например `socks5://host.docker.internal:1301` (порт — ваш на хосте).
2. **TelegramConflictError** — с тем же `TELEGRAM_TOKEN` уже запущен другой long polling (локально `bot-dev`, второй Docker и т.д.). Остановите лишний процесс.
3. **401 по токену** — неверный `TELEGRAM_TOKEN` или в `bot/.env` строка с **CRLF** / лишними символами (в коде токен и строки из env **trim**-ятся).

Смотреть причину:

```bash
docker compose --profile app logs bot --tail 80
```

## Если `backend` в статусе `unhealthy`

Пока в entrypoint идёт **`alembic upgrade head`**, uvicorn ещё не слушает порт **8000** — healthcheck не должен считать это ошибкой: в [`docker-compose.yml`](../../docker-compose.yml) у `backend` задан **`start_period: 300s`**. Если после пяти минут всё ещё unhealthy, смотрите логи:

```bash
docker compose --profile app logs backend --tail 200
```

Типичные причины: ошибка миграций, в контейнере всё ещё уходит `DATABASE_URL` на **127.0.0.1** (тогда Alembic не достучится до Postgres — entrypoint принудительно выставляет URL на сервис **`postgres`**, см. `DOCKER_DATABASE_URL` в compose), **CRLF** в `devops/backend/docker-entrypoint.sh` на Windows (образ при сборке выполняет `sed` для LF; в репозитории для `*.sh` задан `.gitattributes`).

После правок Dockerfile/entrypoint пересоберите backend: **`.\tasks.ps1 stack-build`** или `docker compose --profile app build backend`, затем снова **`stack-up`**.

Из PowerShell при Docker только в WSL: **`.\tasks.ps1 stack-rebuild-backend-wsl`** — `docker compose --profile app down` и `build backend --no-cache` через `wsl` и каталог репозитория в виде `/mnt/<буква>/...` (пути с кириллицей не через `wslpath` из PowerShell — см. `Get-RepoRootWslPath` в `tasks.ps1`).
