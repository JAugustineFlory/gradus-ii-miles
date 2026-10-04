"""Shared fixtures for every backend test.

Provided by GRADUS II. You don't need to change this file.

- engine:  a connection to the TEST database, with every table created
           fresh before each test and dropped after it
- session: an AsyncSession on that database (for model tests)
- client:  an httpx AsyncClient whose requests reach the app, with the
           app's get_db dependency pointed at the test database
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app import models  # noqa: F401  (registers tables with Base)
from app.config import get_test_database_url
from app.database import Base, get_db
from app.main import app


@pytest.fixture
async def engine():
    engine = create_async_engine(get_test_database_url(), poolclass=NullPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session(engine):
    TestingSession = async_sessionmaker(engine, expire_on_commit=False)
    async with TestingSession() as db:
        yield db


@pytest.fixture
async def client(engine):
    TestingSession = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with TestingSession() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()
