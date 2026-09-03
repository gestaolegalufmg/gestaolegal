"""add acao and descricao columns to historicos

Revision ID: a1b2c3d4e5f6
Revises: 03085453841c
Create Date: 2026-07-02 21:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "03085453841c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("historicos", sa.Column("acao", sa.String(50), nullable=True))
    op.add_column("historicos", sa.Column("descricao", sa.String(500), nullable=True))


def downgrade():
    op.drop_column("historicos", "descricao")
    op.drop_column("historicos", "acao")
