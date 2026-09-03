"""notificações: destino estruturado, lida e data/hora

A tabela `notificacao` vem da v2 (executor, destinatário, texto da ação e
data) e nunca foi removida. Para o módulo voltar na 3.0 ela ganha o destino
estruturado (tipo + ids, em vez de interpretar o texto), a marcação de lida e
a data/hora de criação.

Revision ID: 2101e3af25b9
Revises: 4e1eb1a09578
Create Date: 2026-09-03 11:00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2101e3af25b9"
down_revision = "4e1eb1a09578"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("notificacao", sa.Column("tipo", sa.String(length=30), nullable=True))
    op.add_column("notificacao", sa.Column("id_caso", sa.Integer(), nullable=True))
    op.add_column("notificacao", sa.Column("id_referencia", sa.Integer(), nullable=True))
    op.add_column(
        "notificacao",
        sa.Column("lida", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("notificacao", sa.Column("data_criacao", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("notificacao", "data_criacao")
    op.drop_column("notificacao", "lida")
    op.drop_column("notificacao", "id_referencia")
    op.drop_column("notificacao", "id_caso")
    op.drop_column("notificacao", "tipo")
