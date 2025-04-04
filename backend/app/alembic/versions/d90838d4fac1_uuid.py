"""UUID

Revision ID: d90838d4fac1
Revises: 41bb0413ccef
Create Date: 2025-03-31 05:21:10.560536

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "d90838d4fac1"
down_revision = "41bb0413ccef"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("button_created_by_fkey", "button", type_="foreignkey")
    op.create_foreign_key(
        None, "button", "user", ["created_by"], ["id"], ondelete="SET DEFAULT"
    )
    op.drop_constraint(
        "buttonretirement_created_by_fkey", "buttonretirement", type_="foreignkey"
    )
    op.drop_constraint(
        "buttonretirement_button_id_fkey", "buttonretirement", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "buttonretirement", "button", ["button_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        None, "buttonretirement", "user", ["created_by"], ["id"], ondelete="SET DEFAULT"
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "buttonretirement", type_="foreignkey")
    op.drop_constraint(None, "buttonretirement", type_="foreignkey")
    op.create_foreign_key(
        "buttonretirement_button_id_fkey",
        "buttonretirement",
        "button",
        ["button_id"],
        ["id"],
    )
    op.create_foreign_key(
        "buttonretirement_created_by_fkey",
        "buttonretirement",
        "user",
        ["created_by"],
        ["id"],
    )
    op.drop_constraint(None, "button", type_="foreignkey")
    op.create_foreign_key(
        "button_created_by_fkey",
        "button",
        "user",
        ["created_by"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###
