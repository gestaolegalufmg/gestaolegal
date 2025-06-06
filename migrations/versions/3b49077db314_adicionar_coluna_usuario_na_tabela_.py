"""adicionar coluna usuario na tabela orientacao_juridica

Revision ID: 3b49077db314
Revises: ed1b0a0a61a6
Create Date: 2023-10-25 06:06:35.372156

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3b49077db314"
down_revision = "ed1b0a0a61a6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "orientacao_juridica", sa.Column("id_usuario", sa.Integer, nullable=True)
    )


def downgrade():
    op.drop_column("orientacao_juridica", "id_usuario")
