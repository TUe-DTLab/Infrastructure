"""Create new models

Revision ID: e829a27e94a2
Revises: 
Create Date: 2023-08-14 02:40:52.649745

"""
import fastapi_users_db_sqlalchemy
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "e829a27e94a2"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "models", sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.PrimaryKeyConstraint("id")
    )
    op.create_table(
        "projects", sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.PrimaryKeyConstraint("id")
    )
    op.create_table(
        "schemas",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("json_schema", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "user",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("id", fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
        sa.Column("graphdb_username", sa.String(), nullable=True),
        sa.Column("graphdb_password", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_table(
        "accesstoken",
        sa.Column("token", sa.String(length=43), nullable=False),
        sa.Column("created_at", fastapi_users_db_sqlalchemy.generics.TIMESTAMPAware(timezone=True), nullable=False),
        sa.Column("user_id", fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("token"),
    )
    op.create_index(op.f("ix_accesstoken_created_at"), "accesstoken", ["created_at"], unique=False)
    op.create_table(
        "datasources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.Enum("none", "float", "vector3", "json", name="datasourceenum"), nullable=True),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["model_id"], ["models.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "file_objects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["model_id"], ["models.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("path"),
    )
    op.create_table(
        "roles_model",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.Enum("guest", "maintainer", "admin", name="roleenum_model"), nullable=True),
        sa.ForeignKeyConstraint(["model_id"], ["models.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "model_id"),
    )
    op.create_table(
        "roles_project",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.Enum("guest", "maintainer", "admin", name="roleenum_project"), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "project_id"),
    )
    op.create_table(
        "datasources_float",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["datasources.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "datasources_vector3",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["id"],
            ["datasources.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "datapoints_float",
        sa.Column("datetime", sa.DateTime(), nullable=False),
        sa.Column("datasource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["datasource_id"], ["datasources_float.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("datetime", "datasource_id"),
    )
    op.create_table(
        "datapoints_vector3",
        sa.Column("datetime", sa.DateTime(), nullable=False),
        sa.Column("datasource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("x", sa.Float(), nullable=True),
        sa.Column("y", sa.Float(), nullable=True),
        sa.Column("z", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["datasource_id"], ["datasources_vector3.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("datetime", "datasource_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("datapoints_vector3")
    op.drop_table("datapoints_float")
    op.drop_table("datasources_vector3")
    op.drop_table("datasources_float")
    op.drop_table("roles_project")
    op.drop_table("roles_model")
    op.drop_table("file_objects")
    op.drop_table("datasources")
    op.drop_index(op.f("ix_accesstoken_created_at"), table_name="accesstoken")
    op.drop_table("accesstoken")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
    op.drop_table("schemas")
    op.drop_table("projects")
    op.drop_table("models")
    # ### end Alembic commands ###
