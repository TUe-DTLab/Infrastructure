"""Change file field

Revision ID: 6f5e833430a2
Revises: e825c57c050b
Create Date: 2023-08-15 16:46:39.744335

"""
import fastapi_users_db_sqlalchemy
import sqlalchemy as sa
import sqlalchemy_file

from alembic import op

# revision identifiers, used by Alembic.
revision = "6f5e833430a2"
down_revision = "e825c57c050b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("datapoints_float_datetime_idx", table_name="datapoints_float")
    op.drop_index("datapoints_json_datetime_idx", table_name="datapoints_json")
    op.drop_index("datapoints_vector3_datetime_idx", table_name="datapoints_vector3")
    op.add_column("file_objects", sa.Column("file", sqlalchemy_file.types.FileField(), nullable=True))
    op.drop_constraint("file_objects_path_key", "file_objects", type_="unique")
    op.drop_column("file_objects", "path")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("file_objects", sa.Column("path", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_unique_constraint("file_objects_path_key", "file_objects", ["path"])
    op.drop_column("file_objects", "file")
    op.create_index("datapoints_vector3_datetime_idx", "datapoints_vector3", [sa.text("datetime DESC")], unique=False)
    op.create_index("datapoints_json_datetime_idx", "datapoints_json", [sa.text("datetime DESC")], unique=False)
    op.create_index("datapoints_float_datetime_idx", "datapoints_float", [sa.text("datetime DESC")], unique=False)
    # ### end Alembic commands ###
