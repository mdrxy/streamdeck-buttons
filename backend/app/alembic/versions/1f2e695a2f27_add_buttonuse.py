"""Add ButtonUse

Revision ID: 1f2e695a2f27
Revises: ff9de6948801
Create Date: 2025-03-31 00:03:22.154626

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "1f2e695a2f27"
down_revision = "ff9de6948801"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "buttonuse",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("button_id", sa.Uuid(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column(
            "origin", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["button_id"],
            ["button.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("buttonuse")
    # ### end Alembic commands ###
