.PHONY: install run lint format test test-backend ci-check help \
	backend-test backend-dev \
	backend-lint backend-typecheck \
	db-up db-down db-reset db-migrate db-migrate-test-db db-migrate-all \
	db-test-create db-migrate-test db-shell db-status migrate-backend migrate-backend-test \
	stack-up stack-down stack-up-ghcr stack-down-ghcr stack-status stack-logs stack-build \
	stack-rebuild-backend-wsl \
	check-backend check-web check-bot \
	frontend-install frontend-dev frontend-lint frontend-build

# Опционально: имя сервиса для `make stack-logs` (postgres | backend | web | bot). Пусто — все сервисы.
STACK_SERVICE ?=

# Команда Compose: по умолчанию локальный `docker compose`.
# Если Docker доступен только в WSL (в PowerShell/CMD `docker` не находится), задайте, например:
#   make db-up DOCKER_COMPOSE="wsl -e docker compose"
# Надёжнее — открыть WSL, перейти в каталог репозитория и вызывать `make db-up` без переопределения.
#
# Смешанный режим (Docker в WSL, uv на Windows): поднять БД — из WSL
#   wsl -e bash -lc 'cd "/mnt/c/.../repo" && docker compose up -d --wait'
# миграции и alembic current — с хоста с заданным DATABASE_URL (см. docs/tech/db-tooling-guide.md).
DOCKER_COMPOSE ?= docker compose

POSTGRES_USER ?= llmstart
POSTGRES_PASSWORD ?= llmstart
POSTGRES_DB ?= llmstart
POSTGRES_TEST_DB ?= llmstart_test
DATABASE_URL ?= postgresql+asyncpg://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@127.0.0.1:5432/$(POSTGRES_DB)
TEST_DATABASE_URL ?= postgresql+asyncpg://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@127.0.0.1:5432/$(POSTGRES_TEST_DB)
export DATABASE_URL TEST_DATABASE_URL

help:
	@echo "Основные цели (подробнее: docs/tech/docker-compose-local.md):"
	@echo "  db-up / db-down / db-reset   — только PostgreSQL из compose + миграции Alembic с хоста"
	@echo "  stack-up / stack-down       — полный стек (профиль app: backend, web, bot)"
	@echo "  stack-up-ghcr / stack-down-ghcr — тот же стек из образов GHCR (docker-compose.ghcr.yml; см. docs/tech/docker-compose-ghcr.md)"
	@echo "  stack-status / stack-logs   — диагностика compose (STACK_SERVICE=web для одного сервиса)"
	@echo "  stack-build                 — docker compose build --profile app"
	@echo "  stack-rebuild-backend-wsl   — down + build backend --no-cache (DOCKER_COMPOSE, см. tasks.ps1)"
	@echo "  check-backend / check-web / check-bot — HTTP-проверки на localhost (нужен curl)"
	@echo "  install, lint, test-backend, backend-dev, frontend-*, ci-check — см. Makefile"

install:
	uv sync --group dev
	cd backend && uv sync --extra dev

run:
	uv run python -m bot.main

lint:
	uv run ruff check bot
	uv run ruff format --check bot
	cd backend && uv run --extra dev ruff check app tests && uv run --extra dev ruff format --check app tests

# Статическая часть CI: ruff + ESLint + next build (нужны зависимости: make install; для фронта — make frontend-install).
ci-check: lint frontend-lint frontend-build

format:
	uv run ruff format bot
	uv run ruff check --fix bot
	cd backend && uv run --extra dev ruff format app tests && uv run --extra dev ruff check --fix app tests

test: test-backend

# PostgreSQL (tests/pg), нужен llmstart_test и TEST_DATABASE_URL.
test-backend:
	cd backend && uv sync --extra dev && uv run pytest tests/pg

# Если том Postgres уже создан без init-скрипта — создать БД для pytest (идемпотентно через grep).
db-test-create:
	@$(DOCKER_COMPOSE) exec -T -e PGPASSWORD=$(POSTGRES_PASSWORD) postgres \
		psql -U $(POSTGRES_USER) -d postgres -tc "SELECT 1 FROM pg_database WHERE datname='$(POSTGRES_TEST_DB)'" | grep -q 1 || \
	$(DOCKER_COMPOSE) exec -T -e PGPASSWORD=$(POSTGRES_PASSWORD) postgres \
		psql -U $(POSTGRES_USER) -d postgres -c "CREATE DATABASE $(POSTGRES_TEST_DB) OWNER $(POSTGRES_USER);"

backend-test: test-backend

# Нужен PostgreSQL на DATABASE_URL (локально: сначала make db-up). На Windows см. tasks.ps1 backend-dev — проверка порта 5432.
backend-dev:
	cd backend && uv sync && uv run uvicorn app.main:app --reload

backend-lint: lint

# Проверка типов: в проекте пока нет mypy; цель зарезервирована под tasklist-database (DoD).
backend-typecheck:
	@echo "backend-typecheck: mypy не настроен в backend/pyproject.toml; используйте ruff (make lint)."

# Только Postgres из compose (профиль app не трогаем) + Alembic на llmstart и llmstart_test с хоста.
db-up:
	$(DOCKER_COMPOSE) up -d --wait postgres
	$(MAKE) db-migrate-all

db-down:
	$(DOCKER_COMPOSE) down

db-reset:
	$(DOCKER_COMPOSE) down -v
	$(DOCKER_COMPOSE) up -d --wait postgres
	$(MAKE) db-migrate-all

# Полный локальный стек в Docker (нужны backend/.env, bot/.env; опционально BACKEND_API_CLIENT_TOKEN в окружении для web).
stack-up:
	$(DOCKER_COMPOSE) --profile app up -d --wait

# Образы из GHCR: в .env или окружении задайте LLMSTART_GHCR_IMAGE_ROOT (см. .env.ghcr.example).
stack-up-ghcr:
	$(DOCKER_COMPOSE) -f docker-compose.ghcr.yml --profile app up -d --wait

stack-down:
	$(DOCKER_COMPOSE) --profile app down

stack-down-ghcr:
	$(DOCKER_COMPOSE) -f docker-compose.ghcr.yml --profile app down

stack-status:
	$(DOCKER_COMPOSE) ps -a

stack-logs:
	@test -z "$(STACK_SERVICE)" && $(DOCKER_COMPOSE) --profile app logs -f \
		|| $(DOCKER_COMPOSE) --profile app logs -f $(STACK_SERVICE)

stack-build:
	$(DOCKER_COMPOSE) --profile app build

# Только WSL в имени: из PowerShell удобнее .\tasks.ps1 stack-rebuild-backend-wsl.
# Здесь: тот же DOCKER_COMPOSE, что для db-up (задайте wsl -e docker compose при необходимости).
stack-rebuild-backend-wsl:
	$(DOCKER_COMPOSE) --profile app down
	$(DOCKER_COMPOSE) --profile app build backend --no-cache

check-backend:
	@curl -fsS http://127.0.0.1:8000/health >/dev/null && echo "OK: GET http://127.0.0.1:8000/health"

check-web:
	@curl -fsS -o /dev/null http://127.0.0.1:3000/ && echo "OK: GET http://127.0.0.1:3000/"

check-bot:
	@$(DOCKER_COMPOSE) --profile app exec -T bot python -c "import urllib.request; urllib.request.urlopen('http://backend:8000/health', timeout=5)" && echo "OK: bot container -> backend /health"

# Явный DATABASE_URL + --no-env-file: миграции к Docker Postgres, без подмешивания чужого .env.
db-migrate:
	cd backend && uv sync --extra dev && \
	DATABASE_URL=postgresql+asyncpg://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@127.0.0.1:5432/$(POSTGRES_DB) \
	uv run --no-env-file alembic upgrade head

# Та же цепочка миграций на БД для pytest (пустая в pgAdmin без этого шага).
db-migrate-test-db:
	cd backend && uv sync --extra dev && \
	DATABASE_URL=postgresql+asyncpg://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@127.0.0.1:5432/$(POSTGRES_TEST_DB) \
	uv run --no-env-file alembic upgrade head

# Основная БД + при необходимости создание llmstart_test + миграции на тестовую БД (нужен запущенный compose).
# Ревизия Alembic 0007 добавляет демо-когорту `demo_frontend_mvp` (преподаватель akozhin, telegram_user_id 162684825).
db-migrate-all: db-migrate db-test-create db-migrate-test-db

migrate-backend: db-migrate

# После db-up: миграции на обе БД, pytest на Postgres (TEST_DATABASE_URL).
db-migrate-test: db-migrate-all test-backend

migrate-backend-test: db-migrate-test

db-shell:
	$(DOCKER_COMPOSE) exec -e PGPASSWORD=$(POSTGRES_PASSWORD) postgres \
		psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

db-status:
	$(DOCKER_COMPOSE) ps -a
	@echo "--- Проверьте, что у сервиса postgres в PORTS есть 0.0.0.0:5432->5432/tcp"

# Веб-клиент (Next.js): см. frontend/web/.env.example и README.
frontend-install:
	cd frontend/web && pnpm install

frontend-dev:
	cd frontend/web && pnpm dev

frontend-lint:
	cd frontend/web && pnpm lint

frontend-build:
	cd frontend/web && pnpm build
