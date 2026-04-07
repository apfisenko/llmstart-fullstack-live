.PHONY: install run lint format test test-backend migrate-backend

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

migrate-backend:
	cd backend && uv sync --extra dev && uv run alembic upgrade head
