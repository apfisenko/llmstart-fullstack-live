"""Общие плагины для tests/pg."""

import os

# api_fixtures импортирует app.main до pytest_configure в tests/pg — подставляем URL заранее.
if os.environ.get("TEST_DATABASE_URL") and not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]

pytest_plugins = ["tests.api_fixtures"]
