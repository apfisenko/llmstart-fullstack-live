from __future__ import annotations

import os

# make test-backend / CI: TEST_DATABASE_URL → отдельная БД (*_test), не llmstart.
if os.environ.get("TEST_DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]

import pytest

from app.config import get_settings


def _database_name_from_url(url: str) -> str | None:
    if "://" not in url:
        return None
    rest = url.split("://", 1)[1]
    if "/" not in rest:
        return None
    path = rest.split("/", 1)[1]
    name = path.split("?", 1)[0].strip()
    return name or None


def pytest_configure(config: pytest.Config) -> None:  # noqa: ARG001
    get_settings.cache_clear()
    url = get_settings().database_url
    if not url.startswith("postgresql"):
        pytest.exit(
            "Suite tests/pg requires PostgreSQL. "
            "Use: make test-backend (or pytest tests/pg). "
            "For SQLite: make test-backend-sqlite (pytest tests/sqlite).",
            returncode=1,
        )
    dbn = _database_name_from_url(url)
    if not dbn or not dbn.endswith("_test"):
        pytest.exit(
            "PostgreSQL for tests/pg must be a disposable DB whose name ends with _test "
            f"(e.g. llmstart_test). Current database name: {dbn!r}.",
            returncode=1,
        )
