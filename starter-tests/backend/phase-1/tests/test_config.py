"""Configuration comes from environment variables, with safe defaults.

`monkeypatch` is a built-in pytest fixture. It changes things (here,
environment variables) for one test only and undoes the change after.
"""

from app.config import (
    get_database_url,
    get_frontend_origin,
    get_test_database_url,
)

LOCAL = "postgresql+asyncpg://miles:miles@localhost:5434"


def test_database_url_defaults_to_local_dev_database(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    assert get_database_url() == f"{LOCAL}/miles"


def test_database_url_can_be_overridden(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://x:y@db:5432/z")

    assert get_database_url() == "postgresql+asyncpg://x:y@db:5432/z"


def test_test_database_url_defaults_to_local_test_database(monkeypatch):
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)

    assert get_test_database_url() == f"{LOCAL}/miles_test"


def test_test_database_url_can_be_overridden(monkeypatch):
    monkeypatch.setenv("TEST_DATABASE_URL", "postgresql+asyncpg://x:y@db/t")

    assert get_test_database_url() == "postgresql+asyncpg://x:y@db/t"


def test_frontend_origin_defaults_to_vite_dev_server(monkeypatch):
    monkeypatch.delenv("FRONTEND_ORIGIN", raising=False)

    assert get_frontend_origin() == "http://localhost:5173"


def test_frontend_origin_can_be_overridden(monkeypatch):
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://localhost:3000")

    assert get_frontend_origin() == "http://localhost:3000"
