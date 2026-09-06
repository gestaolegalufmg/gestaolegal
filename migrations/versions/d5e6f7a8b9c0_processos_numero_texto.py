"""Preserva pontuação e zeros iniciais dos números de processo."""

import re

import sqlalchemy as sa
from alembic import op

revision = "d5e6f7a8b9c0"
down_revision = "c4d5e6f7a8b9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "processos",
        "numero",
        existing_type=sa.BigInteger(),
        type_=sa.String(25),
        existing_nullable=True,
    )


def downgrade() -> None:
    conn = op.get_bind()
    numeros = conn.execute(
        sa.text("SELECT numero FROM processos WHERE numero IS NOT NULL")
    ).scalars()
    for numero in numeros:
        # Só converte representações canônicas que cabem em BIGINT assinado.
        if (
            not re.fullmatch(r"0|-?[1-9][0-9]*", numero)
            or not -(2**63) <= int(numero) < 2**63
        ):
            raise RuntimeError(
                "Downgrade abortado: processos.numero contém valores que "
                "perderiam informação ao converter para BIGINT."
            )
    op.alter_column(
        "processos",
        "numero",
        existing_type=sa.String(25),
        type_=sa.BigInteger(),
        existing_nullable=True,
    )
