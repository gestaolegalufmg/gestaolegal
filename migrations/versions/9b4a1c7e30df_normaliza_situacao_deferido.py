"""casos: normaliza a situação legada "deferido" para "ativo"

Revision ID: 9b4a1c7e30df
Revises: 7c3d5b9f21ae
Create Date: 2026-09-03

Casos gravados antes da normalização ficaram com "deferido", valor que não
existe mais na lista de situações. O formulário de edição rejeitava esses
casos com "invalid input" no campo Situação do Deferimento.
"""

from alembic import op

revision = "9b4a1c7e30df"
down_revision = "7c3d5b9f21ae"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "UPDATE casos SET situacao_deferimento = 'ativo' "
        "WHERE situacao_deferimento = 'deferido'"
    )


def downgrade() -> None:
    # Não há como distinguir os casos que já eram "ativo" dos convertidos.
    pass
