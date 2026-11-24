"""Shared fixtures: a fresh test database and a rolled-back session per test."""

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import NullPool, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.settings import Settings

TEST_DB_NAME = "jobhunt_test"
ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


async def _recreate_database(admin_url: str) -> None:
    # CREATE/DROP DATABASE can't run inside a transaction, hence AUTOCOMMIT.
    engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME} WITH (FORCE)"))
        await conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))
    await engine.dispose()


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Once per test run: drop and recreate jobhunt_test, then migrate it to head."""
    dev_url = make_url(Settings().database_url)
    admin_url = dev_url.set(database="postgres")
    test_url = dev_url.set(database=TEST_DB_NAME)

    asyncio.run(_recreate_database(admin_url.render_as_string(hide_password=False)))

    url = test_url.render_as_string(hide_password=False)
    config = Config(ALEMBIC_INI)
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    return url


@pytest.fixture
async def session(test_db_url: str) -> AsyncIterator[AsyncSession]:
    """A session inside a transaction that is rolled back after the test."""
    engine = create_async_engine(test_db_url, poolclass=NullPool)
    async with engine.connect() as conn:
        transaction = await conn.begin()
        # Commits inside the test only release a savepoint; the outer
        # transaction still gets rolled back, so every test starts empty.
        db = AsyncSession(bind=conn, join_transaction_mode="create_savepoint")
        try:
            yield db
        finally:
            await db.close()
            await transaction.rollback()
    await engine.dispose()
