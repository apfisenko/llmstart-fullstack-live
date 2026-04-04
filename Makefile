.PHONY: install run lint format

install:
	python -m pip install -r requirements.txt

run:
	python -m bot.main

lint:
	python -m ruff check .
	python -m ruff format --check .

format:
	python -m ruff format .
	python -m ruff check --fix .
