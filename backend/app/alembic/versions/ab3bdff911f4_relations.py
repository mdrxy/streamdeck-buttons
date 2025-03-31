"""Relations

Revision ID: ab3bdff911f4
Revises: d443da0e1c3e
Create Date: 2025-03-31 03:27:33.418599

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "ab3bdff911f4"
down_revision = "d443da0e1c3e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("buttonuse_button_id_fkey", "buttonuse", type_="foreignkey")
    op.create_foreign_key(
        None, "buttonuse", "button", ["button_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "buttonuse", type_="foreignkey")
    op.create_foreign_key(
        "buttonuse_button_id_fkey", "buttonuse", "button", ["button_id"], ["id"]
    )
    # ### end Alembic commands ###
