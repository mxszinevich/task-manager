from typing import AsyncGenerator, Callable

import alembic
from alembic.config import Config
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import PostgresDsn
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_utils import create_database, drop_database

from api.dependencies.db import get_db_session
from api.dependencies.users import get_active_user, get_user
from config import settings
from db.session import AsyncSessionBuilder

pytest_plugins = (
    "tests.fixtures.users",
    "tests.fixtures.tasks",
    "tests.fixtures.categories",
    "tests.fixtures.tasks_categories",
)

faker = Faker(locale="ru_RU")


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale():
    return ["ru_RU"]


@pytest.fixture()
def test_postgres_dsn() -> Callable:
    def build_dsn(**kwargs) -> str:
        db_name = "_".join((s.lower() for s in settings.app.name.split(" ")))
        test_db_dsn = PostgresDsn.build(
            scheme=kwargs.get("scheme") or settings.db.scheme,
            user=kwargs.get("user") or settings.db.user,
            password=kwargs.get("password") or settings.db.password,
            host=kwargs.get("host") or settings.db.host,
            port=kwargs.get("port") or settings.db.port,
            path=f"/pytest_{db_name}",
        )
        return test_db_dsn

    return build_dsn


@pytest.fixture()
def create_db(test_postgres_dsn):
    dsn: str = test_postgres_dsn(scheme="postgresql")
    try:
        create_database(dsn)
        yield
    finally:
        drop_database(dsn)


@pytest.fixture(autouse=True)
def apply_migrations(create_db, test_postgres_dsn):
    config = Config("alembic.ini")
    config.set_section_option(config.config_ini_section, "sqlalchemy.url", test_postgres_dsn(scheme=settings.db.scheme))
    alembic.command.upgrade(config, "head")
    yield


@pytest.fixture()
def test_session(test_postgres_dsn) -> AsyncSession:
    test_db_dsn = test_postgres_dsn(scheme=settings.db.scheme)
    async_session_builder = AsyncSessionBuilder(database_url=test_db_dsn, echo=settings.db.echo)
    yield async_session_builder()


@pytest.fixture()
async def override_get_db_session(test_session) -> AsyncGenerator:
    async def get_db():
        async with test_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()

    return get_db


@pytest.fixture()
def app(override_get_db_session) -> FastAPI:
    from main import app as app_

    app_.dependency_overrides[get_db_session] = override_get_db_session
    yield app_


@pytest.fixture()
async def test_client(app: FastAPI) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture()
async def test_cred_client(app: FastAPI, user_active) -> AsyncGenerator:
    async def _get_user():
        return user_active

    app.dependency_overrides[get_active_user] = _get_user
    app.dependency_overrides[get_user] = _get_user
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        try:
            yield client
        finally:
            app.dependency_overrides.pop(get_active_user)
            app.dependency_overrides.pop(get_user)
