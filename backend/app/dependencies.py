import asyncio
import base64
import uuid
from typing import Optional

import requests
from fastapi import Depends, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy_oso import authorized_sessionmaker

from app import models

# from app.dependencies import get_access_token_db, get_user_db
from app.config import config
from app.models import AccessToken, User

api_key_header = APIKeyHeader(name=config["API_KEY_NAME"], auto_error=True)


SCOPES = [
    "admin",
    "project:read",
    "project:write",
    "project:delete",
]


async def get_async_db():
    from app.database import engine_async

    async with sessionmaker(bind=engine_async, expire_on_commit=False, future=True, class_=AsyncSession)() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_db)):
    yield SQLAlchemyUserDatabase(session, models.User)


async def get_access_token_db(session: AsyncSession = Depends(get_async_db)):
    yield SQLAlchemyAccessTokenDatabase(session, models.AccessToken)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


def get_database_strategy(access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db)):
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = config["SECRET"]

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
        # Register user on graphdb
        credentials = "%s:%s" % (config["GRAPHDB_USER"], config["GRAPHDB_PASSWD"])
        headers = {"Authorization": "Basic %s" % base64.b64encode(credentials.encode("utf-8")).decode("utf-8")}
        payload = {
            "password": user.graphdb_password,
            "appSettings": {
                "DEFAULT_SAMEAS": True,
                "DEFAULT_INFERENCE": True,
                "EXECUTE_COUNT": True,
                "IGNORE_SHARED_QUERIES": False,
                "DEFAULT_VIS_GRAPH_SCHEMA": True,
            },
            "grantedAuthorities": ["ROLE_USER"],
        }
        requests.post(
            f"{config['GRAPHDB_URL']}/rest/security/users/{user.graphdb_username}", json=payload, headers=headers
        )

    async def on_before_delete(self, user: User, request: Optional[Request] = None):
        # Deregister user from graphdb
        credentials = "%s:%s" % (config["GRAPHDB_USER"], config["GRAPHDB_PASSWD"])
        headers = {"Authorization": "Basic %s" % base64.b64encode(credentials.encode("utf-8")).decode("utf-8")}
        request.delete(f"{config['GRAPHDB_URL']}/rest/security/users/{user.graphdb_username}", headers=headers)

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


auth_backend = AuthenticationBackend(
    name="database",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_user_admin = fastapi_users.current_user(active=True, superuser=True)


def get_current_user(request: Request):
    loop = asyncio.get_event_loop()
    coroutine = current_active_user()
    loop.run_until_complete(coroutine)


class GetDatabase:
    def __init__(self, checked_permissions: dict):
        self.get_checked_permissions = lambda: checked_permissions

    def __call__(self, user: User = Depends(current_active_user)):
        from app.database import engine, oso

        with authorized_sessionmaker(
            get_oso=lambda: oso,
            get_user=lambda: user,
            get_checked_permissions=self.get_checked_permissions,
            bind=engine,
            future=True,
        )() as session:
            yield session
