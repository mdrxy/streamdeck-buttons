"""usage_count and retired_at only exist in Button model

Revision ID: ff9de6948801
Revises: b321ebb8aa47
Create Date: 2025-03-30 23:03:19.206642

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "ff9de6948801"
down_revision = "b321ebb8aa47"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
