"""Configuration comes from environment variables, with safe defaults.

`monkeypatch` is a built-in pytest fixture. It changes things (here,
environment variables) for one test only and undoes the change after.
"""

from app.config import get_database_url, get_frontend_origin


def test_database_url_defaults_to_local_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    assert get_database_url() == "sqlite:///./miles.db"


def test_database_url_can_be_overridden(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./other.db")

    assert get_database_url() == "sqlite:///./other.db"


def test_frontend_origin_defaults_to_vite_dev_server(monkeypatch):
    monkeypatch.delenv("FRONTEND_ORIGIN", raising=False)

    assert get_frontend_origin() == "http://localhost:5173"


def test_frontend_origin_can_be_overridden(monkeypatch):
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://localhost:3000")

    assert get_frontend_origin() == "http://localhost:3000"
