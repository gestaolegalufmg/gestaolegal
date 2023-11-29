"""modificacao de email coluna atendidos

Revision ID: 03085453841c
Revises: 92fb0a220f9b
Create Date: 2023-11-24 05:56:12.970174

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03085453841c'
down_revision = '92fb0a220f9b'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('email', 'atendidos')


def downgrade():
    op.create_index('email', 'atendidos', ['email'],  unique=True)
