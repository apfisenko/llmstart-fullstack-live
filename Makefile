.PHONY: install run lint format

install:
	uv sync --all-groups

run:
	uv run python -m bot.main

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
	uv run ruff check --fix .
