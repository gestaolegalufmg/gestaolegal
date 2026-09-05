"""eventos: amplia `arquivo` de String(100) para String(300)

Revision ID: c4d5e6f7a8b9
Revises: b7c1d2e3f4a5
Create Date: 2026-09-05

Com os anexos saindo da pasta estática para o volume privado, `eventos.arquivo`
passa a guardar a referência relativa do arquivo dentro da raiz privada, e não
mais só o nome. Os 100 caracteres da coluna são curtos demais para isso —
`arquivosCaso.link_arquivo` e `arquivos.caminho` já são String(300).

A migration só altera o tipo da coluna: nenhum arquivo é movido ou reescrito.
"""

import sqlalchemy as sa
from alembic import op

revision = "c4d5e6f7a8b9"
down_revision = "b7c1d2e3f4a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "eventos",
        "arquivo",
        existing_type=sa.String(length=100),
        type_=sa.String(length=300),
        existing_nullable=True,
    )


def downgrade() -> None:
    # Reduzir para 100 truncaria silenciosamente as referências relativas já
    # gravadas. Recusa a redução se houver alguma acima do limite antigo.
    conn = op.get_bind()
    excedentes = conn.execute(
        sa.text(
            "SELECT COUNT(*) FROM eventos "
            "WHERE arquivo IS NOT NULL AND LENGTH(arquivo) > 100"
        )
    ).scalar()
    if excedentes:
        raise RuntimeError(
            f"downgrade abortado: {excedentes} registro(s) em eventos.arquivo "
            "excedem 100 caracteres e seriam truncados. Mova ou encurte essas "
            "referências antes de reduzir a coluna."
        )
    op.alter_column(
        "eventos",
        "arquivo",
        existing_type=sa.String(length=300),
        type_=sa.String(length=100),
        existing_nullable=True,
    )
