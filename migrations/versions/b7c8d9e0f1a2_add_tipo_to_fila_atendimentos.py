"""add tipo column to fila_atendimentos

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-07-02 22:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b7c8d9e0f1a2"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "fila_atendimentos", sa.Column("tipo", sa.String(80), nullable=True)
    )


def downgrade():
    op.drop_column("fila_atendimentos", "tipo")
