from __future__ import annotations

import os

import pytest

from app.config import get_settings


def pytest_configure(config: pytest.Config) -> None:  # noqa: ARG001
    os.environ.pop("TEST_DATABASE_URL", None)
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    get_settings.cache_clear()
    url = get_settings().database_url
    if not url.startswith("sqlite"):
        pytest.exit("Suite tests/sqlite requires SQLite URL.", returncode=1)
