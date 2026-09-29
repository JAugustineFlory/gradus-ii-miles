"""Shared fixtures for every backend test.

Provided by GRADUS II. You don't need to change this file.

- engine:  a fresh in-memory SQLite database with every table created
- session: a SQLAlchemy session on that database (for model tests)
- client:  a TestClient whose requests use that same database
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registers tables with Base)
from app.database import Base, get_db
from app.main import app


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine):
    with Session(engine) as db:
        yield db


@pytest.fixture
def client(engine):
    TestingSession = sessionmaker(
        bind=engine,
        autoflush=False,
    )

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
