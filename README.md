# LLMStart — Система сопровождения учебного потока

Платформа помощи студентам и преподавателю курса **AI-driven Fullstack Developer**: навигация по программе, ответы по содержанию, фиксация прогресса.

> Учебный проект курса. Разрабатывается участниками потока в рамках программы.

## О проекте

Студенты курса теряют ориентиры: где материалы, что дальше, как зафиксировать результат.  
Система даёт единую точку входа через Telegram-бота и веб-кабинет.  
Ключевые пользователи: **студент** — навигация и прогресс; **преподаватель** — обзор потока.

## Архитектура

```mermaid
flowchart LR
  subgraph clients["Клиенты"]
    TG["Telegram-бот\n(bot/)"]
    WEB["Веб-приложение\n(frontend/web)"]
  end
  subgraph core["Ядро"]
    BE["Backend API\n(backend/)"]
    DB[("PostgreSQL")]
    LLM["LLM\n(OpenRouter)"]
  end
  TG -->|HTTP| BE
  WEB -->|HTTP| BE
  BE --> DB
  BE --> LLM
```

Бизнес-логика живёт только в `backend/`. Бот (`bot/`) и веб (`frontend/web/`) — тонкие клиенты без уникальных правил.

Обзор компонентов, схемы и ссылки на ADR — [docs/architecture.md](docs/architecture.md). Продуктовые границы — [docs/vision.md](docs/vision.md).

## Статус

Дорожная карта и статусы итераций — [docs/plan.md](docs/plan.md).

## Документация

- [Онбординг разработчика](docs/onboarding.md) — клонирование, env, проверка стека, CI-подобные команды
- [Локальный Docker Compose](docs/tech/docker-compose-local.md) — только Postgres или полный стек (`stack-up`), проверки сервисов
- [Стек из образов GHCR](docs/tech/docker-compose-ghcr.md) — запуск без локальной сборки образов приложений (`docker-compose.ghcr.yml`)
- [Архитектура (обзор)](docs/architecture.md)
- [Идея продукта](docs/idea.md)
- [Архитектурное видение](docs/vision.md)
- [Модель данных](docs/data-model.md)
- [Интеграции](docs/integrations.md)
- [План](docs/plan.md)
- [Задачи](docs/tasks/)

Каталог [data/README.md](data/README.md) описывает **программу учебного курса**, а не runtime приложения LLMStart.

## Требования к окружению

Минимальный набор совпадает с [CI](.github/workflows/ci.yml):

| Инструмент | Версия / ориентир |
|------------|-------------------|
| Node.js | **22** |
| pnpm | **10** (в CI задаётся `pnpm/action-setup`) |
| uv | актуальная stable ([документация uv](https://docs.astral.sh/uv/)) |
| Docker + Compose | локальный Postgres (`db-up`) или полный стек — [docker-compose-local.md](docs/tech/docker-compose-local.md) |
| Python | то, что задаёт корневой и `backend/` проект через uv |

Шаблоны переменных окружения **только у компонентов**: [`backend/.env.example`](backend/.env.example), [`bot/.env.example`](bot/.env.example), [`frontend/web/.env.example`](frontend/web/.env.example) — корневого `.env.example` в репозитории нет.

## Быстрый старт

Нужен [uv](https://docs.astral.sh/uv/) (корень и `backend/` синхронизируются через lock-файлы).

В **Linux/macOS** или при установленном [GNU Make](https://www.gnu.org/software/make/) удобны цели из [Makefile](Makefile). В **Windows** (PowerShell/cmd) команда `make` часто отсутствует — используйте скрипт **[`tasks.ps1`](tasks.ps1)** (аналог Makefile), команды из раздела [ниже](#windows-no-make) или поставьте Make (например [Chocolatey: `make`](https://community.chocolatey.org/packages/make), пакет MSYS2, Git Bash с make, [WSL](https://learn.microsoft.com/windows/wsl/)).

**Перед PR:** из корня после `make install` и `make frontend-install` выполните **`make ci-check`** (ruff + ESLint + сборка фронта, как статическая часть CI) и **`make test-backend`** (нужен Postgres) — или **`.\tasks.ps1 ci-check`**, **`.\tasks.ps1 test-backend`**. Полный порядок шагов совпадает с [`.github/workflows/ci.yml`](.github/workflows/ci.yml): зависимости → `pnpm lint` / `pnpm build` во `frontend/web` → ruff → `pytest tests/pg`. **Юнит-тестов у фронта нет** — не ищите `pnpm test`.

<a id="windows-no-make"></a>

### Запуск без make (Windows)

#### Скрипт `tasks.ps1` (как Makefile)

Все перечисленные ниже цели для Windows — только **`tasks.ps1`** (аналог `Makefile`): `install`, **`bot-dev`**, `lint`, `format`, `db-up`, `backend-dev`, `frontend-dev` и др. Раньше в корне лежал отдельный `run.ps1` с урезанным набором команд — он убран в пользу **`tasks.ps1`**.

Из **корня** репозитория, в **PowerShell** (нужны **uv**; для `db-*` — **docker** в PATH или задайте `$env:DOCKER_COMPOSE = 'wsl -e docker compose'`):

```powershell
.\tasks.ps1 help          # список целей
.\tasks.ps1 install
.\tasks.ps1 frontend-install
.\tasks.ps1 ci-check       # ruff + pnpm lint + pnpm build (как статика в CI)
.\tasks.ps1 test-backend   # pytest tests/pg (нужен Postgres)
.\tasks.ps1 db-up          # compose + миграции на llmstart и llmstart_test
# при уже запущенном Postgres только основная БД: .\tasks.ps1 db-migrate
.\tasks.ps1 frontend-install   # зависимости Next.js (frontend/web)
.\tasks.ps1 frontend-dev       # веб на http://127.0.0.1:3000 (нужен pnpm)
.\tasks.ps1 bot-dev            # Telegram-бот (как make run)
```

Нужны **[pnpm](https://pnpm.io/)** и **Node.js 22** (как в CI) для `frontend/web/`. Файл окружения веба: скопируйте [`frontend/web/.env.example`](frontend/web/.env.example) → **`frontend/web/.env.local`**, задайте **`BACKEND_ORIGIN`**. Если в **`backend/.env`** включён **`BACKEND_API_CLIENT_TOKEN`**, продублируйте то же значение во **`frontend/web/.env.local`** — иначе для входа через веб токен не нужен. Затем поднимите backend и откройте страницу входа.

Краткий happy-path: [docs/onboarding.md](docs/onboarding.md) (разделы 2–3).

После полного `alembic upgrade head` ревизия **`0007`** (если ещё не применена) создаёт демо-поток с `cohorts.code = demo_frontend_mvp`: преподаватель **`telegram_username` akozhin**, **`telegram_user_id` 162684825**, студенты `demo_student_alpha` / `beta` / `gamma`, чекпоинты (в т.ч. ДЗ), прогресс и реплики в диалогах для KPI и веб-экранов.

**Вход преподавателя (MVP, веб / ручная проверка API):**

1. Поднимите PostgreSQL и накатите миграции (**`.\tasks.ps1 db-up`** или **`make db-up`**), затем запустите backend из **`backend/`** (см. раздел [Backend API](#backend-api) ниже).
2. Вызовите **`POST /api/v1/auth/dev-session`** с телом **`{"telegram_username": "akozhin"}`** (допустимо и **`@akozhin`** — сервер приводит имя к одному виду). Базовый URL, например: `http://127.0.0.1:8000`.
3. Если в **`backend/.env`** задан **`BACKEND_API_CLIENT_TOKEN`**, к запросу добавьте заголовок **`Authorization: Bearer <тот же токен>`**.
4. В ответе используйте участие с **`role`: `teacher`**: его **`membership_id`** передавайте как **`viewer_membership_id`** в **`GET /api/v1/cohorts/{cohort_id}/teacher-dashboard`** и **`GET .../summary`**. **`cohort_id`** возьмите из того же элемента `memberships` (или из таблицы для быстрых ручных вызовов ниже).

| Для ручных вызовов | UUID |
|--------------------|------|
| Демо-когорта `demo_frontend_mvp` | `f1eef000-0000-4000-8000-000000000001` |
| Участие преподавателя (teacher) | `f1eef000-0000-4000-8000-000000000011` |

Подробнее по контракту: [`docs/tech/api-contracts.md`](docs/tech/api-contracts.md), интерактивно — **`/docs`** на запущенном backend.

Если выполнение скриптов запрещено политикой: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (один раз). Переменные **`DOCKER_COMPOSE`**, **`POSTGRES_*`**, **`POSTGRES_TEST_DB`**, **`DATABASE_URL`**, **`TEST_DATABASE_URL`** — те же, что в [Makefile](Makefile).

#### Команды вручную

Из **корня** репозитория — то же, что делают цели `Makefile`:

| Цель `make` | Команды |
|-------------|---------|
| `install` | `uv sync --group dev`, затем в `backend\`: `uv sync --extra dev` |
| `ci-check` | `lint`, затем `frontend-lint`, затем `frontend-build` (статическая часть CI; сначала один раз `frontend-install`) |
| `run` | `uv run python -m bot.main` |
| `lint` | `uv run ruff check bot` и `uv run ruff format --check bot`; затем в `backend\`: `uv run --extra dev ruff check app tests` и `uv run --extra dev ruff format --check app tests` |
| `format` | `uv run ruff format bot` и `uv run ruff check --fix bot`; затем в `backend\`: `uv run --extra dev ruff format app tests` и `uv run --extra dev ruff check --fix app tests` |
| `test` / `test-backend` / `test-all` | в `backend\`: `uv sync --extra dev`, `uv run pytest tests/pg` (Postgres `*_test`; `tasks.ps1` выставляет `TEST_DATABASE_URL`) |
| `migrate-backend` | в `backend\`: `uv sync --extra dev`, затем `uv run alembic upgrade head` (только **`POSTGRES_DB`**) |
| `db-migrate-test` | `db-migrate-all`, затем `test-backend` (pytest на **`TEST_DATABASE_URL`** → обычно `llmstart_test`). |

В **cmd** одной строкой для backend (как в Makefile): `cd backend && uv sync --extra dev && uv run pytest` и `cd backend && uv sync --extra dev && uv run alembic upgrade head`. В **PowerShell 5.1** надёжнее три отдельные строки (`cd backend`, `uv sync ...`, `uv run ...`); в **PowerShell 7+** допустим оператор `&&`.

**Без uv (только рантайм бота):** `python -m pip install -r requirements.txt` — без `ruff` и pytest; для полной проверки качества используйте `uv` и строки выше.

### Backend API

Нужен файл окружения (зависимости — через `make install` или `uv sync` в `backend/`). Конфиг backend ([`backend/app/config.py`](backend/app/config.py)) читает **`backend/.env`** (`env_file=".env"` при запуске из каталога `backend/`). Строка **`DATABASE_URL`** (PostgreSQL) задаётся только там.

1. Шаблон backend — [`backend/.env.example`](backend/.env.example) → **`backend/.env`**. Бот — [`bot/.env.example`](bot/.env.example) → **`bot/.env`**; конфиг бота подгружается **только** оттуда (не из `backend/.env`).
2. Установить зависимости и запустить сервер из каталога `backend/`:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

`BACKEND_HOST` и `BACKEND_PORT` в **`backend/.env`** должны совпадать с аргументами `--host` / `--port` у uvicorn.

Для **тестов** и **миграций Alembic** нужен dev-набор: `uv sync --extra dev`.

**База данных:** только **PostgreSQL**. В **`backend/.env`** задайте **`DATABASE_URL`** (`postgresql+asyncpg://...`). Схема — через **Alembic**: из **корня** репозитория **`make migrate-backend`** (внутри: `cd backend && uv sync --extra dev && uv run alembic upgrade head`). На Windows без make — **`.\tasks.ps1 db-migrate`** или строка **`migrate-backend`** в [таблице выше](#windows-no-make).

На **Windows**, если **Docker** только в **WSL**, поднимайте Postgres из WSL, **Alembic** — с `DATABASE_URL` на `127.0.0.1:5432`, **pytest** — с **`TEST_DATABASE_URL`** на БД `*_test` (например `llmstart_test`): это делает **`make test-backend`** / **`.\tasks.ps1 test-backend`** (см. [docs/tech/db-tooling-guide.md](docs/tech/db-tooling-guide.md), «Смешанный режим»). Цель **`make db-migrate-test`**: миграции основной БД, при необходимости создание тестовой БД, затем тесты.

**`connection refused` / `10061` на `127.0.0.1:5432`:** на этом порту никто не слушает — чаще всего **не запущен** контейнер Postgres. Из корня репозитория выполните **`.\tasks.ps1 db-up`** (или **`make db-up`**), дождитесь healthy. Команда **`.\tasks.ps1 backend-dev`** перед uvicorn **ждёт порт 5432** (25 с) и выведет подсказку, если БД недоступна; для удалённой БД задайте **`LLMSTART_SKIP_POSTGRES_WAIT=1`**. Убедитесь, что **Docker Desktop** запущен и в **`backend/.env`** **`DATABASE_URL`** указывает на тот же хост и порт, что пробросил compose (по умолчанию `postgresql+asyncpg://llmstart:llmstart@127.0.0.1:5432/llmstart`).

**Проверка после запуска:**

- `GET http://127.0.0.1:8000/health` → `{"status":"ok"}` (подставьте свой хост/порт).
- Документация API: **Swagger** `/docs`, машиночитаемая схема **`GET /openapi.json`**, **ReDoc** `/redoc`.
- Публичное API: префикс `/api/v1/`.

**Тесты backend** (из корня): **`make test`** или **`make test-backend`** (одинаковые). На Windows без make — строка **`test`** в [таблице выше](#windows-no-make).

**Линт и формат:** **`make lint`** / **`make format`** — сначала пакет `bot/` (корневой `pyproject.toml`), затем `backend/app` и `backend/tests` (настройки [backend/pyproject.toml](backend/pyproject.toml)). Детали — [backend/README.md](backend/README.md).

### Telegram-бот

Бот ходит только в **backend API** (LLM на стороне ядра). **Запуск** достаточно с `TELEGRAM_TOKEN` и поднятым backend. **`COHORT_ID` и `MEMBERSHIP_ID` не обязательны:** в этом случае используется **guest-режим** (`POST /api/v1/assistant/guest/*`) — диалог в памяти процесса backend, без строк в БД; сценарий позже можно сменить на поток/membership. Если оба UUID заданы и данные есть в БД, запросы идут в основной контракт `.../cohorts/{id}/dialogues/messages` с персистентностью.

Проверка **Telegram username** через тот же контракт, что и веб-вход: команды **`/username имя`** (без пробелов в аргументе) и **`/login`** (бот попросит ввести username следующим сообщением). Если на backend включён Bearer, в **`bot/.env`** задайте **`BACKEND_API_CLIENT_TOKEN`** (как для остальных вызовов API).

**Локально (PostgreSQL):** после **`make db-up`** и **`make migrate-backend`** выполните демо-вставки в БД (например **`make db-shell`** или клиент к `DATABASE_URL`). Подставьте свои UUID в **`bot/.env`** или оставьте эти и скопируйте в `COHORT_ID` / `MEMBERSHIP_ID`:

```sql
INSERT INTO users (id, telegram_user_id, name)
VALUES ('11111111-1111-1111-1111-111111111111', NULL, 'Demo');
INSERT INTO cohorts (id, title, code)
VALUES ('22222222-2222-2222-2222-222222222222', 'Demo cohort', 'demo');
INSERT INTO cohort_memberships (id, user_id, cohort_id, role, status)
VALUES (
  '33333333-3333-3333-3333-333333333333',
  '11111111-1111-1111-1111-111111111111',
  '22222222-2222-2222-2222-222222222222',
  'student',
  'active'
);
```

Тогда в **`bot/.env`**: `COHORT_ID=22222222-2222-2222-2222-222222222222`, `MEMBERSHIP_ID=33333333-3333-3333-3333-333333333333`.

Скопировать [`bot/.env.example`](bot/.env.example) → **`bot/.env`** и задать **`TELEGRAM_TOKEN`**. **`COHORT_ID` / `MEMBERSHIP_ID`** нужны только для режима с БД (SQL ниже); без них работает guest-LLM через тот же backend. Если включён Bearer для API, добавьте в **`bot/.env`** **`BACKEND_API_CLIENT_TOKEN`** из [`backend/.env.example`](backend/.env.example) (значение должно совпадать с backend). Параметры LLM для процесса backend — там же в `backend/.env.example` (**`OPENROUTER_API_KEY`** и др.; пустой ключ → заглушка). Из **корня** репозитория:

```bash
make install
make run
```

Без make (Windows): **`.\tasks.ps1 install`** и **`.\tasks.ps1 bot-dev`** (аналог **`make install`** / **`make run`**); либо команды из [таблицы выше](#windows-no-make).

На MVP один `MEMBERSHIP_ID` в **`bot/.env`** используется для всех пользователей Telegram; для продакшена нужна отдельная привязка аккаунтов.

`PROXY_URL` в **`bot/.env`** используется **только для Telegram** (aiogram). Запросы бота к `BACKEND_BASE_URL` идут **напрямую**; отдельный прокси для backend — переменная `BACKEND_HTTP_PROXY` (см. [`bot/.env.example`](bot/.env.example)).

**Если бот «молчит» или нет ответа на текст:**

1. **Пишите в личку боту**, не в группу: в группах включена **privacy mode** — бот не видит обычные сообщения, только команды и упоминания. В коде бота ответ в группе заменён на подсказку открыть личный чат.
2. **Backend запущен** и доступен с машины, где крутится бот: `GET http://127.0.0.1:8000/health` (или ваш `BACKEND_BASE_URL`). Иначе бот ответит строкой про недоступность сервера.
3. Если в `backend/.env` задан **`BACKEND_API_CLIENT_TOKEN`**, в **`bot/.env`** должно быть **то же значение** — иначе `401` и ответ «Нет доступа к сервису».
4. У **@BotFather** для бота не должен быть активен **webhook**, если вы используете **polling** (`make run`): при необходимости сбросьте webhook через Bot API или @BotFather.
5. **`PROXY_URL`** (только Telegram): если задан неверный или недоступный прокси, запросы к Telegram API зависают и падают с `ProxyTimeoutError` — оставьте переменную **пустой**, если прокси не нужен.
6. Ответ бота «Не удалось получить ответ» при **502** от backend: смотрите лог **uvicorn** — строка `llm_upstream_4xx` с подсказкой от провайдера. Обычно это неверный или пустой **`OPENROUTER_API_KEY`**, лимит, имя модели или блокировка исходящего HTTPS (в т.ч. **`PROXY_URL`** в `backend/.env` для вызова OpenRouter).

Запускайте бота из репозитория через **`uv run python -m bot.main`** (как в `make run`), а не глобальный Python с устаревшими пакетами в `AppData\Roaming\Python`.

### Локальный полный стек из образов GHCR

Поднимаете **PostgreSQL, backend, web и bot** из образов в **GitHub Container Registry** — без `docker build` приложений на машине. Сборка и push выполняются workflow [`.github/workflows/ghcr.yml`](.github/workflows/ghcr.yml) после **успешного CI** на **`main`** / **`master`** (или вручную в Actions). Имена образов и теги — [devops/README.md](devops/README.md), подробности и логин при приватных пакетах — [docs/tech/docker-compose-ghcr.md](docs/tech/docker-compose-ghcr.md).

1. **Корень образов** в нижнем регистре: `ghcr.io/<владелец>/<репозиторий>` (как в GitHub после публикации пакетов). Задайте переменную **`LLMSTART_GHCR_IMAGE_ROOT`** и при необходимости **`IMAGE_TAG`** (`latest` по умолчанию; ещё бывают теги вида `sha-<short>`). Удобно скопировать [`.env.ghcr.example`](.env.ghcr.example) в **корневой `.env`** (файл не коммитится) или экспортировать переменные в shell перед `compose up`.
2. **Секреты и конфиг**, как для обычного полного стека в Docker: подготовьте **`backend/.env`** и **`bot/.env`** по шаблонам из разделов [Backend API](#backend-api) и [Telegram-бот](#telegram-бот). Если в `backend/.env` включён **`BACKEND_API_CLIENT_TOKEN`**, задайте то же значение в окружении хоста и при необходимости в корневом **`.env`**, чтобы подставилось в сервис **web** (см. таблицу в [docs/tech/docker-compose-local.md](docs/tech/docker-compose-local.md)).
3. **Запуск из корня репозитория:** **`make stack-up-ghcr`** или **`.\tasks.ps1 stack-up-ghcr`**. Используется файл [`docker-compose.ghcr.yml`](docker-compose.ghcr.yml). Остановка профиля приложений: **`make stack-down-ghcr`** / **`.\tasks.ps1 stack-down-ghcr`**.
4. **Windows, Docker только в WSL:** **`.\tasks.ps1 stack-up-ghcr-wsl`** и **`stack-down-ghcr-wsl`** (аналогично `stack-up-wsl`; см. [docker-compose-ghcr.md](docs/tech/docker-compose-ghcr.md)).

После старта: веб **http://127.0.0.1:3000**, API **http://127.0.0.1:8000** (`/health`, `/docs`). Проверки: **`make check-backend`**, **`make check-web`**, **`make check-bot`** или те же цели в **`tasks.ps1`**.

### Полный стек (бот + backend + CI)

Пайплайн на push/PR в ветках `main`/`master` — [`.github/workflows/ci.yml`](.github/workflows/ci.yml): установка зависимостей, **`pnpm lint`** и **`pnpm build`** в `frontend/web/`, затем **ruff** по `bot/` и `backend/`, затем **`pytest tests/pg`** на PostgreSQL. Локально то же разумно повторить как **`make ci-check`** (или `.\tasks.ps1 ci-check`) и **`make test-backend`**. Дорожная карта — [`docs/plan.md`](docs/plan.md); задача **08** в [tasklist-backend](docs/tasks/tasklist-backend.md) закрывает единый `Makefile` и CI на уровне репозитория.
