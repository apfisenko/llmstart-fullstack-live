# Онбординг разработчика

Цель: за один сеанс клонировать репозиторий, настроить окружение и убедиться, что backend, БД и (по желанию) веб работают. Версии инструментов как в CI — [.github/workflows/ci.yml](../.github/workflows/ci.yml) (Node **22**, pnpm **10**, uv, Postgres **16** в сервисе CI).

Архитектура монорепо — [architecture.md](architecture.md). Продовый VPS (Timeweb, `twc`, SSH) — [tech/timeweb-vps.md](tech/timeweb-vps.md); **ручной** подъём стека с образов GHCR на хосте — [tech/vps-manual-ghcr-deploy.md](tech/vps-manual-ghcr-deploy.md). Обзор итераций DevOps — [tasks/tasklist-devops.md](tasks/tasklist-devops.md).

**Команды из корня репозитория**

- **Windows (PowerShell):** `.\tasks.ps1 <цель>` — полный список: `.\tasks.ps1 help`. Это основной способ для разработки на Windows; `make` в типичной установке отсутствует.
- **Linux / macOS / WSL с GNU Make:** те же цели через `make <цель>` из [Makefile](../Makefile) — удобно при переносе проекта в среду Linux или если вы сознательно пользуетесь Make в WSL из каталога репозитория.

Ниже в примерах сначала вариант **Windows** (`.\tasks.ps1`), затем при необходимости — **make** для Unix-подобных сред.

---

## 1. Клонирование и первичная настройка

1. Клонируйте репозиторий.
2. Установите инструменты (минимум для backend и линта):

   | Инструмент | Назначение |
   |------------|------------|
   | [uv](https://docs.astral.sh/uv/) | Python: корень + `backend/` |
   | [Docker](https://docs.docker.com/get-docker/) + Compose | локальный PostgreSQL (`.\tasks.ps1 db-up`; на Linux при наличии Make — `make db-up`) |
   | Node **22** + [pnpm **10**](https://pnpm.io/) | `frontend/web` (как в CI) |

3. Из **корня** репозитория установите зависимости:

   **Windows (PowerShell):**

   ```powershell
   .\tasks.ps1 install
   ```

   **Linux / macOS** (при установленном `make`):

   ```bash
   make install
   ```

   **Ожидание:** команды завершаются без ошибки; в `backend/` появляется виртуальное окружение uv.

---

## 2. Настройка каждого компонента

Шаблоны окружения **только в каталогах компонентов** (корневого `.env.example` нет).

### Backend

1. Скопируйте [`backend/.env.example`](../backend/.env.example) → `backend/.env`.
2. Задайте `DATABASE_URL` под ваш Postgres (после `db-up` по умолчанию: `postgresql+asyncpg://llmstart:llmstart@127.0.0.1:5432/llmstart`).
3. При необходимости заполните LLM и `BACKEND_API_CLIENT_TOKEN` по комментариям в шаблоне.

### База данных

Из корня:

**Windows:**

```powershell
.\tasks.ps1 db-up
```

**Linux / macOS** (с `make`):

```bash
make db-up
```

**Ожидание:** контейнер Postgres healthy; Alembic накатывает миграции на `llmstart` и `llmstart_test`.

### Полный стек в Docker (опционально)

Чтобы поднять **backend**, **web** и **bot** в контейнерах вместе с Postgres, см. [tech/docker-compose-local.md](tech/docker-compose-local.md): `.\tasks.ps1 stack-up` / `make stack-up`, проверки `check-backend`, `check-web`, `check-bot`. Для привычного сценария «Postgres в Docker, uvicorn на хосте» достаточно **`db-up`** без профиля `app`.

### Telegram-бот (опционально)

1. [`bot/.env.example`](../bot/.env.example) → `bot/.env`.
2. `TELEGRAM_TOKEN` от @BotFather; `BACKEND_BASE_URL` на ваш uvicorn.
3. Если на backend включён Bearer — тот же `BACKEND_API_CLIENT_TOKEN`, что в `backend/.env`.

Подробнее: [bot/README.md](../bot/README.md), раздел «Telegram-бот» в [README.md](../README.md).

### Веб (frontend/web)

1. [`frontend/web/.env.example`](../frontend/web/.env.example) → `frontend/web/.env.local`.
2. Обязательно: `BACKEND_ORIGIN=http://127.0.0.1:8000` (без завершающего `/`).
3. Если задан `BACKEND_API_CLIENT_TOKEN` в backend — продублируйте в `.env.local`.

Из корня: **`.\tasks.ps1 frontend-install`** (Windows) или **`make frontend-install`** (Linux с Make).

Либо из каталога `frontend/web/`: `pnpm install`.

---

## 3. Проверка, что всё работает

### Backend

Из каталога `backend/`:

```bash
cd backend && uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Или из **корня** после БД: **`.\tasks.ps1 backend-dev`** (Windows) / **`make backend-dev`** (Linux с Make).

- `curl -s http://127.0.0.1:8000/health` → тело вида `{"status":"ok"}`.
- `curl -s http://127.0.0.1:8000/health/db` — проверка подключения к БД (ожидается успешный JSON, не 5xx).

### Веб

```bash
cd frontend/web && pnpm dev
```

Из корня: **`.\tasks.ps1 frontend-dev`** (Windows) / **`make frontend-dev`** (Linux с Make).

- В логе: готовность Next на `http://127.0.0.1:3000` (или указанный порт).
- В браузере: открыть `/login`. При пустом или неверном `BACKEND_ORIGIN` API-прокси вернут конфигурационную ошибку — см. `frontend/web/lib/server-backend.ts`.

### Сценарий dev-session (преподаватель, демо-данные)

После **`.\tasks.ps1 db-up`** (ревизия Alembic **0007** создаёт демо-когорту) см. пошагово корневой [README.md](../README.md) (блок «Вход преподавателя»): `POST /api/v1/auth/dev-session` с `{"telegram_username": "akozhin"}`.

### Качество как в CI (статика + тесты)

Из **корня** после `install` и `frontend-install`:

**Windows:**

```powershell
.\tasks.ps1 install
.\tasks.ps1 frontend-install
.\tasks.ps1 ci-check
.\tasks.ps1 test-backend
```

**Linux / macOS** (с `make`):

```bash
make install
make frontend-install
make ci-check
make test-backend
```

`ci-check` = ruff (bot + backend) + `pnpm lint` + `pnpm build` в `frontend/web`.  
`test-backend` требует доступный Postgres и `TEST_DATABASE_URL` (как в [Makefile](../Makefile) и в `tasks.ps1`).

**Фронт:** отдельного `pnpm test` в проекте нет — только `lint` и `build`.

---

## 4. Куда смотреть в первую очередь

| Область | Точка входа |
|---------|-------------|
| Backend приложение | `backend/app/main.py` |
| API v1 | `backend/app/api/v1/` |
| Бот | `bot/main.py`, `bot/handlers/`, `bot/services/backend_assistant.py` |
| Веб | `frontend/web/app/`, `frontend/web/app/api/v1/` (прокси к backend) |
| Домен и схема | [data-model.md](data-model.md) |
| План итераций | [plan.md](plan.md) |

---

## 5. Рабочий процесс

Итерации и задачи ведутся по [workflow.mdc](../.cursor/rules/workflow.mdc): области → `docs/tasks/tasklist-*.md` → планы в `docs/tasks/impl/.../plan.md` и итоги `summary.md`. Перед работой — `plan.md`, после — `summary.md`.

---

## 6. Как готовить изменения (проверки качества)

1. Перед коммитом (по договорённости команды): **`.\tasks.ps1 format`** (Windows) или **`make format`** (Linux с Make).
2. Перед PR: **`.\tasks.ps1 ci-check`** и **`.\tasks.ps1 test-backend`**; на Linux с Make — **`make ci-check`** и **`make test-backend`**.
3. Убедитесь, что не коммитите секреты: только локальные `.env` / `.env.local` (в git не попадают по `.gitignore`).

Если **`ci-check`** падает на **ruff** (`E501`, `Would reformat` и т.п.) — из корня сначала **`.\tasks.ps1 format`**, затем снова **`.\tasks.ps1 ci-check`**. Для **backend** `ruff` входит только в optional **`dev`**: при ручном вызове из `backend\` используйте **`uv run --extra dev ruff …`** (в **`tasks.ps1`** и **`Makefile`** это уже заложено в цели `lint` / `format` / `ci-check`).

Полный пайплайн CI: [.github/workflows/ci.yml](../.github/workflows/ci.yml).
