"""empty message

Revision ID: 68eafece20df
Revises: 8f8afd8095dd
Create Date: 2022-01-19 14:25:24.091919

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68eafece20df'
down_revision = '8f8afd8095dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('external_accounts', sa.Column('logo', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('external_accounts', 'logo')
    # ### end Alembic commands ###