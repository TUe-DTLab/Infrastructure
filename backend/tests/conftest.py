import asyncio
import contextlib

import pytest_asyncio
from fastapi import Depends
from fastapi_users.schemas import BaseUserCreate
from httpx import AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_oso import authorized_sessionmaker

from app import models
from app.config import config
from app.database import Base
from app.dependencies import (
    GetDatabase,
    current_active_user,
    get_async_db,
    get_user_db,
    get_user_manager,
)
from app.main import app as fastapiapp

# from app.schemas.users import UserCreate

SQLAlCHEMY_DATABASE_URL = "postgresql://{user}:{password}@{host}:{port}/{name}".format(
    user=config["DATABASE_USER"] + "_test",
    password=config["DATABASE_PASSWORD"],
    host=config["DATABASE_HOST"],
    port=config["DATABASE_PORT"],
    name=config["DATABASE_NAME"] + "_test",
)

SQLAlCHEMY_DATABASE_URL_ASYNC = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}".format(
    user=config["DATABASE_USER"] + "_test",
    password=config["DATABASE_PASSWORD"],
    host=config["DATABASE_HOST"],
    port=config["DATABASE_PORT"],
    name=config["DATABASE_NAME"] + "_test",
)

engine = create_engine(SQLAlCHEMY_DATABASE_URL)
engine_async = create_async_engine(SQLAlCHEMY_DATABASE_URL_ASYNC)

# import app.models  # noqa

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


async def override_get_async_db():
    from tests.conftest import engine_async

    session_maker = sessionmaker(bind=engine_async, expire_on_commit=False, future=True, class_=AsyncSession)

    async with session_maker() as session:
        yield session


def mock_call(self, user: models.User = Depends(current_active_user)):
    # https://aalvarez.me/posts/setting-up-a-sqlalchemy-and-pytest-based-test-suite/
    from app.database import oso

    # from tests.conftest import engine
    # connection = engine.connect()
    # transaction = connection.begin()
    session_maker = authorized_sessionmaker(
        get_oso=lambda: oso,
        get_user=lambda: user,
        get_checked_permissions=self.get_checked_permissions,
        bind=DataBaseConnector.connection,
        future=True,
        autocommit=False,
        autoflush=False,
    )
    with session_maker() as session:
        session.begin_nested()

        @event.listens_for(session, "after_transaction_end")
        def restart_savepoint(db_session, transaction):
            if transaction.nested and not transaction._parent.nested:
                session.expire_all()
                session.begin_nested()

        yield session
        # transaction.rollback()


fastapiapp.dependency_overrides[get_async_db] = override_get_async_db


class DataBaseConnector:
    connection = ""
    transaction = ""


@pytest_asyncio.fixture(scope="function")
def setup_session():
    from tests.conftest import engine

    DataBaseConnector.connection = engine.connect()
    DataBaseConnector.transaction = DataBaseConnector.connection.begin()
    yield
    DataBaseConnector.transaction.rollback()


@pytest_asyncio.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
def patch(monkeypatch):
    monkeypatch.setattr(GetDatabase, "__call__", mock_call)
    yield


class InitialState:
    project = None
    sensor = None


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initdb():
    fastapiapp.dependency_overrides[get_async_db] = override_get_async_db

    get_async_session_context = contextlib.asynccontextmanager(override_get_async_db)
    get_user_db_context = contextlib.asynccontextmanager(get_user_db)
    get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

    async with get_async_session_context() as session:
        async with get_user_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                user = await user_manager.create(
                    BaseUserCreate(email="user@example.com", password="string", is_superuser=True)
                )
                print(f"User created {user}")

    from tests.conftest import engine_async

    session_maker = sessionmaker(bind=engine_async, expire_on_commit=False, future=True, class_=AsyncSession)

    async with session_maker() as db:
        project = models.Project(name="initial-project")
        db.add(project)
        await db.commit()
        await db.refresh(project)
        sensor = models.Sensor(name="initial-sensor", project_id=project.id)
        db.add(sensor)
        await db.commit()
    InitialState.project = project
    InitialState.sensor = sensor


@pytest_asyncio.fixture(scope="session")
async def get_bearer_token():
    user = {"username": "user@example.com", "password": "string"}
    async with AsyncClient(app=fastapiapp, base_url="http://localhost") as ac:
        response = await ac.post("/auth/jwt/login", data=user)
    bearer_token = response.json()["access_token"]
    headers = {"Authorization": "Bearer " + bearer_token}
    return headers
