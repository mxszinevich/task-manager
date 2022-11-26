"""009_alter_category_name

Revision ID: fa8e703c598c
Revises: d0078b7323a9
Create Date: 2022-11-27 00:57:37.540325

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "fa8e703c598c"
down_revision = "d0078b7323a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "categories", ["name"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "categories", type_="unique")
    # ### end Alembic commands ###
