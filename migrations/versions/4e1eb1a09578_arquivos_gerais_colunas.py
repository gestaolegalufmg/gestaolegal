"""arquivos gerais: colunas de caminho, data e autor

A tabela `arquivos` vem da v2 (título, descrição, nome do arquivo) e nunca foi
removida. Para o módulo voltar na 3.0 ela ganha o caminho no disco, a data de
cadastro e quem cadastrou. Registros antigos ficam com essas colunas nulas; o
serviço resolve o caminho deles a partir do nome.

Revision ID: 4e1eb1a09578
Revises: e7f8a9b0c1d2
Create Date: 2026-09-03 09:00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4e1eb1a09578"
down_revision = "e7f8a9b0c1d2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("arquivos", sa.Column("caminho", sa.String(length=300), nullable=True))
    op.add_column("arquivos", sa.Column("data_criacao", sa.DateTime(), nullable=True))
    op.add_column("arquivos", sa.Column("id_criado_por", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_arquivos_criado_por", "arquivos", "usuarios", ["id_criado_por"], ["id"]
    )


def downgrade():
    op.drop_constraint("fk_arquivos_criado_por", "arquivos", type_="foreignkey")
    op.drop_column("arquivos", "id_criado_por")
    op.drop_column("arquivos", "data_criacao")
    op.drop_column("arquivos", "caminho")
