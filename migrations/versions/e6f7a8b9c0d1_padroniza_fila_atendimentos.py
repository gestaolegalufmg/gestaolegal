"""Fila: atendido/data obrigatórios e senha de chamada em UTF-8."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "e6f7a8b9c0d1"
down_revision = "d5e6f7a8b9c0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    incompletos = conn.execute(sa.text(
        "SELECT COUNT(*) FROM fila_atendimentos "
        "WHERE id_atendido IS NULL OR data_criacao IS NULL"
    )).scalar_one()
    if incompletos:
        raise RuntimeError(
            f"Migration abortada: {incompletos} entrada(s) da fila sem atendido "
            "ou data de criação. Corrija os dados antes de tornar os campos obrigatórios."
        )
    op.alter_column(
        "fila_atendimentos", "senha", existing_type=sa.String(10),
        type_=mysql.VARCHAR(10, charset="utf8mb4", collation="utf8mb4_0900_ai_ci"),
        existing_nullable=False,
    )
    op.alter_column(
        "fila_atendimentos", "id_atendido", existing_type=sa.Integer(), nullable=False,
    )
    op.alter_column(
        "fila_atendimentos", "data_criacao", existing_type=sa.DateTime(), nullable=False,
    )


def downgrade() -> None:
    # Restaura a nulabilidade do modelo anterior. Mantém UTF-8: voltar a
    # latin1 poderia perder caracteres gravados após o upgrade.
    op.alter_column(
        "fila_atendimentos", "id_atendido", existing_type=sa.Integer(), nullable=True,
    )
    op.alter_column(
        "fila_atendimentos", "data_criacao", existing_type=sa.DateTime(), nullable=True,
    )
