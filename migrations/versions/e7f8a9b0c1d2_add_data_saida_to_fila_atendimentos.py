"""add data_saida to fila_atendimentos

Revision ID: e7f8a9b0c1d2
Revises: a1b2c3d4e5f6
Create Date: 2026-07-03 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e7f8a9b0c1d2"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "fila_atendimentos",
        sa.Column("data_saida", sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_column("fila_atendimentos", "data_saida")
