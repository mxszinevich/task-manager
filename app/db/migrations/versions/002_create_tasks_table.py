"""002_create_tasks_table

Revision ID: ede5789494a2
Revises: 1f72945ed8e2
Create Date: 2022-11-05 02:10:43.179624

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ede5789494a2"
down_revision = "1f72945ed8e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("body", sa.String(), nullable=True),
        sa.Column("created", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("tasks")
    # ### end Alembic commands ###