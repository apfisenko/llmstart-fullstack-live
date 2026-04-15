.PHONY: install run lint format test test-backend \
	backend-test backend-dev \
	backend-lint backend-typecheck \
	db-up db-down db-reset db-migrate db-migrate-test-db db-migrate-all \
	db-test-create db-migrate-test db-shell db-status migrate-backend migrate-backend-test

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

install:
	uv sync --group dev
	cd backend && uv sync --extra dev

run:
	uv run python -m bot.main

lint:
	uv run ruff check bot
	uv run ruff format --check bot
	cd backend && uv run ruff check app tests && uv run ruff format --check app tests

format:
	uv run ruff format bot
	uv run ruff check --fix bot
	cd backend && uv run ruff format app tests && uv run ruff check --fix app tests

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

# Поднимает Postgres и накатывает Alembic на llmstart и llmstart_test (удобно для GUI-клиентов).
db-up:
	$(DOCKER_COMPOSE) up -d --wait
	$(MAKE) db-migrate-all

db-down:
	$(DOCKER_COMPOSE) down

db-reset:
	$(DOCKER_COMPOSE) down -v
	$(DOCKER_COMPOSE) up -d --wait
	$(MAKE) db-migrate-all

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
