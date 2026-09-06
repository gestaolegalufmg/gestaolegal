"""Preserva anexos cujo binário já estava ausente no acervo de origem."""

import sqlalchemy as sa
from alembic import op

revision = "b9c0d1e2f3a4"
down_revision = "a8b9c0d1e2f3"
branch_labels = None
depends_on = None


def upgrade():
    for nome in ("arquivosCaso", "arquivosEvento"):
        op.add_column(nome, sa.Column("indisponivel_origem", sa.Boolean(),
                                     nullable=False, server_default=sa.false()))


def downgrade():
    conn = op.get_bind()
    for nome in ("arquivosCaso", "arquivosEvento"):
        if conn.execute(sa.text(f"SELECT COUNT(*) FROM `{nome}` WHERE indisponivel_origem=1")).scalar_one():
            raise RuntimeError("Downgrade perderia a indicação de anexos indisponíveis na origem.")
    for nome in ("arquivosCaso", "arquivosEvento"):
        op.drop_column(nome, "indisponivel_origem")
