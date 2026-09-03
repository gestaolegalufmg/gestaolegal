"""notificacao: coluna data_arquivamento

Revision ID: 3f8c2d61b45a
Revises: 9b4a1c7e30df
Create Date: 2026-09-03

"""

import sqlalchemy as sa
from alembic import op

revision = "3f8c2d61b45a"
down_revision = "9b4a1c7e30df"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "notificacao", sa.Column("data_arquivamento", sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("notificacao", "data_arquivamento")
