"""Preserva centavos nos valores da causa."""
import sqlalchemy as sa
from alembic import op

revision = "c0d1e2f3a4b5"
down_revision = "b9c0d1e2f3a4"
branch_labels = None
depends_on = None


def upgrade():
    for name in ("valor_causa_inicial", "valor_causa_atual"):
        op.alter_column("processos", name, existing_type=sa.Integer(),
                        type_=sa.Numeric(15, 2), existing_nullable=True)


def downgrade():
    conn = op.get_bind()
    for name in ("valor_causa_inicial", "valor_causa_atual"):
        if conn.execute(sa.text(f"SELECT COUNT(*) FROM processos WHERE `{name}` != FLOOR(`{name}`) OR `{name}` < -2147483648 OR `{name}` > 2147483647")).scalar_one():
            raise RuntimeError("Downgrade perderia centavos ou valores fora da faixa de inteiro.")
    for name in ("valor_causa_inicial", "valor_causa_atual"):
        op.alter_column("processos", name, existing_type=sa.Numeric(15, 2),
                        type_=sa.Integer(), existing_nullable=True)
