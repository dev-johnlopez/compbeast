"""empty message

Revision ID: cca1be337528
Revises: 3ec9297438f2
Create Date: 2021-10-07 08:34:46.290980

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cca1be337528'
down_revision = '3ec9297438f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('entry_fee', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('event', 'entry_fee')
    # ### end Alembic commands ###
