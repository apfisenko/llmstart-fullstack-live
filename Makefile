.PHONY: install run lint format test test-backend backend-test backend-dev \
	backend-lint backend-typecheck \
	db-up db-down db-reset db-migrate db-migrate-test db-shell migrate-backend migrate-backend-test

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
DATABASE_URL ?= postgresql+asyncpg://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@127.0.0.1:5432/$(POSTGRES_DB)
export DATABASE_URL

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

test-backend:
	cd backend && uv sync --extra dev && uv run pytest

backend-test: test-backend

backend-dev:
	cd backend && uv sync && uv run uvicorn app.main:app --reload

backend-lint: lint

# Проверка типов: в проекте пока нет mypy; цель зарезервирована под tasklist-database (DoD).
backend-typecheck:
	@echo "backend-typecheck: mypy не настроен в backend/pyproject.toml; используйте ruff (make lint)."

db-up:
	$(DOCKER_COMPOSE) up -d --wait

db-down:
	$(DOCKER_COMPOSE) down

db-reset:
	$(DOCKER_COMPOSE) down -v
	$(DOCKER_COMPOSE) up -d --wait
	$(MAKE) db-migrate

db-migrate:
	cd backend && uv sync --extra dev && uv run alembic upgrade head

migrate-backend: db-migrate

# После db-up: миграции до head + unit-тесты backend (pytest использует SQLite in-memory, см. conftest).
db-migrate-test: db-migrate test-backend

migrate-backend-test: db-migrate-test

db-shell:
	$(DOCKER_COMPOSE) exec -e PGPASSWORD=$(POSTGRES_PASSWORD) postgres \
		psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)
