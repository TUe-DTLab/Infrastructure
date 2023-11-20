"""Create timescaledb hypertables

Revision ID: e825c57c050b
Revises: 26889f7b209c
Create Date: 2023-08-14 02:45:45.512217

"""
import fastapi_users_db_sqlalchemy
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "e825c57c050b"
down_revision = "26889f7b209c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("SELECT create_hypertable('datapoints_float', 'datetime', migrate_data => true)")
    op.execute("SELECT create_hypertable('datapoints_vector3', 'datetime', migrate_data => true)")
    op.execute("SELECT create_hypertable('datapoints_json', 'datetime', migrate_data => true)")


def downgrade():
    pass
