import enum
import uuid
from datetime import datetime

from alembic_utils.pg_function import PGFunction
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID
from sqlalchemy import CheckConstraint, Column, Enum, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Float
from sqlalchemy_file import FileField
from sqlalchemy_oso import register_models

from app.database import Base, oso

entities = []


def generate_creds():
    return str(uuid.uuid4())


class User(SQLAlchemyBaseUserTableUUID, Base):
    graphdb_username = Column(String, default=generate_creds)
    graphdb_password = Column(String, default=generate_creds)

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    user_data = Column(JSONB, nullable=True)

    project_roles = relationship("RoleProject", back_populates="user", lazy="joined", cascade="all, delete-orphan")
    model_roles = relationship("RoleModel", back_populates="user", lazy="joined", cascade="all, delete-orphan")


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    pass


class RoleEnum(str, enum.Enum):
    guest = "guest"
    maintainer = "maintainer"
    admin = "admin"


class RoleProject(Base):
    __tablename__ = "roles_project"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), primary_key=True)

    role = Column(Enum(RoleEnum, name="roleenum_project"))

    user = relationship("User", back_populates="project_roles")
    project = relationship("Project", back_populates="members", lazy="joined")


class RoleModel(Base):
    __tablename__ = "roles_model"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), primary_key=True)

    role = Column(Enum(RoleEnum, name="roleenum_model"))

    user = relationship("User", back_populates="model_roles")
    model = relationship("Model", back_populates="members", lazy="joined")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public = Column(Boolean, nullable=False, default=False)

    members = relationship("RoleProject", back_populates="project", cascade="all, delete-orphan")


class Model(Base):
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public = Column(Boolean, nullable=False, default=False)

    members = relationship("RoleModel", back_populates="model", cascade="all, delete-orphan")


class FileObject(Base):
    __tablename__ = "file_objects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    file = Column(FileField)

    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"))


class DataSourceEnum(str, enum.Enum):
    none = "none"
    float = "float"
    vector3 = "vector3"
    json = "json"


class DataSource(Base):
    __tablename__ = "datasources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(DataSourceEnum))
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"))
    name = Column(String)

    UniqueConstraint("name", "model_id", name="UniqueNameInModel")

    __mapper_args__ = {
        "polymorphic_identity": DataSourceEnum.none,
        "polymorphic_on": type,
    }


class DataSourceFloat(DataSource):
    __tablename__ = "datasources_float"

    id = Column(UUID(as_uuid=True), ForeignKey("datasources.id"), primary_key=True)

    data = relationship(
        "DataPointFloat", back_populates="datasource", order_by="DataPointFloat.datetime", cascade="all, delete-orphan"
    )

    __mapper_args__ = {"polymorphic_identity": DataSourceEnum.float}


class DataPointFloat(Base):
    __tablename__ = "datapoints_float"

    datetime = Column(DateTime, primary_key=True)
    datasource_id = Column(UUID(as_uuid=True), ForeignKey("datasources_float.id", ondelete="CASCADE"), primary_key=True)
    value = Column(Float)

    datasource = relationship("DataSourceFloat", back_populates="data")


class DataSourceVector3(DataSource):
    __tablename__ = "datasources_vector3"

    id = Column(UUID(as_uuid=True), ForeignKey("datasources.id"), primary_key=True)

    data = relationship(
        "DataPointVector3",
        back_populates="datasource",
        order_by="DataPointVector3.datetime",
        cascade="all, delete-orphan",
    )

    __mapper_args__ = {"polymorphic_identity": DataSourceEnum.vector3}


class DataPointVector3(Base):
    __tablename__ = "datapoints_vector3"

    datetime = Column(DateTime, primary_key=True)
    datasource_id = Column(
        UUID(as_uuid=True), ForeignKey("datasources_vector3.id", ondelete="CASCADE"), primary_key=True
    )
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)

    datasource = relationship("DataSourceVector3", back_populates="data")


class Schema(Base):
    __tablename__ = "schemas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)
    json_schema = Column(JSON)


class DataSourceJSON(DataSource):
    __tablename__ = "datasources_json"

    id = Column(UUID(as_uuid=True), ForeignKey("datasources.id"), primary_key=True)
    schema_id = Column(UUID(as_uuid=True), ForeignKey("schemas.id"))

    __mapper_args__ = {"polymorphic_identity": DataSourceEnum.json}


class DataPointJSON(Base):
    __tablename__ = "datapoints_json"

    datetime = Column(DateTime, primary_key=True)
    datasource_id = Column(UUID(as_uuid=True), ForeignKey("datasources_json.id", ondelete="CASCADE"), primary_key=True)
    payload = Column(JSONB)

    __table_args__ = (
        CheckConstraint("jsonb_matches_schema(get_schema(datasource_id), payload)", name="check_json_valid"),
    )


get_schema = PGFunction(
    schema="public",
    signature="get_schema(datasource_id uuid)",
    definition="""
    RETURNS json as
    $$
      SELECT schemas.json_schema
      FROM schemas, datasources_json
      WHERE schemas.id = datasources_json.schema_id AND datasources_json.id = datasource_id;
    $$ language SQL;
    """,
)
entities.append(get_schema)


register_models(oso, Base)
oso.load_files(["./policy.polar"])
