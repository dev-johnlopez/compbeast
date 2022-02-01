"""empty message

Revision ID: 66b58214760c
Revises: 0fbdc28f8326
Create Date: 2022-02-01 11:29:05.234147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66b58214760c'
down_revision = '0fbdc28f8326'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('referrer', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'referrer')
    # ### end Alembic commands ###