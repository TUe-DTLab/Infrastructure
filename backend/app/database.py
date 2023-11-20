import os

from fastapi import HTTPException
from libcloud.storage.drivers.local import LocalStorageDriver
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_file.storage import StorageManager
from sqlalchemy_oso import SQLAlchemyOso

from app.config import config

SQLAlCHEMY_DATABASE_URL = "postgresql://{user}:{password}@{host}:{port}/{name}".format(
    user=config["DATABASE_USER"],
    password=config["DATABASE_PASSWORD"],
    host=config["DATABASE_HOST"],
    port=config["DATABASE_PORT"],
    name=config["DATABASE_NAME"],
)

SQLAlCHEMY_DATABASE_URL_ASYNC = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}".format(
    user=config["DATABASE_USER"],
    password=config["DATABASE_PASSWORD"],
    host=config["DATABASE_HOST"],
    port=config["DATABASE_PORT"],
    name=config["DATABASE_NAME"],
)

Base = declarative_base()


def not_found():
    raise HTTPException(status_code=404, detail="Object not found")


def forbidden():
    raise HTTPException(status_code=403, detail="Forbidden")


oso = SQLAlchemyOso(Base)
oso.not_found_error = not_found
oso.forbidden_error = forbidden

engine = create_engine(SQLAlCHEMY_DATABASE_URL)
engine_async = create_async_engine(SQLAlCHEMY_DATABASE_URL_ASYNC)

# Configure file storage
os.makedirs(config["MEDIA_ROOT"] + "/uploaded_files", 0o777, exist_ok=True)
container = LocalStorageDriver(config["MEDIA_ROOT"]).get_container("uploaded_files")
StorageManager.add_storage("default", container)
