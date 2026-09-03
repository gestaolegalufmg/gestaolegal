"""notificacao: coluna detalhe

Revision ID: 7c3d5b9f21ae
Revises: 2101e3af25b9
Create Date: 2026-09-03

"""

import sqlalchemy as sa
from alembic import op

revision = "7c3d5b9f21ae"
down_revision = "2101e3af25b9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("notificacao", sa.Column("detalhe", sa.String(300), nullable=True))


def downgrade() -> None:
    op.drop_column("notificacao", "detalhe")
