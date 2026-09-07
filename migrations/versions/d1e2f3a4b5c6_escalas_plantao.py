"""Escalas por unidade, preservando o legado sem inferir períodos."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import LONGTEXT

revision = "d1e2f3a4b5c6"
down_revision = "c0d1e2f3a4b5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "plantao",
        sa.Column(
            "nome", sa.String(150), nullable=False, server_default="Escala de plantão"
        ),
    )
    op.add_column(
        "plantao",
        sa.Column("legado", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "plantao",
        sa.Column("cancelado", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "plantao",
        sa.Column(
            "historico", sa.Text().with_variant(LONGTEXT(), "mysql"), nullable=True
        ),
    )
    for name in ("dias_plantao", "dias_marcados_plantao"):
        op.add_column(name, sa.Column("plantao_id", sa.Integer(), nullable=True))
    conn = op.get_bind()
    meta = sa.MetaData()
    p, d, m = [
        sa.Table(n, meta, autoload_with=conn)
        for n in ("plantao", "dias_plantao", "dias_marcados_plantao")
    ]
    units = set(conn.execute(sa.select(p.c.unidade_id)).scalars())
    for table in (d, m):
        units.update(conn.execute(sa.select(table.c.unidade_id)).scalars())
    for unit in sorted(units):
        ids = list(
            conn.execute(
                sa.select(p.c.id).where(p.c.unidade_id == unit).order_by(p.c.id)
            ).scalars()
        )
        if not ids:
            ids = [
                conn.execute(
                    p.insert().values(
                        unidade_id=unit,
                        nome="Legado — períodos não identificados",
                        legado=True,
                    )
                ).inserted_primary_key[0]
            ]
        for ident in ids:
            conn.execute(
                p.update()
                .where(p.c.id == ident)
                .values(nome=f"Legado — configuração #{ident}", legado=True)
            )
        # O schema antigo não permite atribuir os dias a períodos: manter juntos
        # em um agrupamento explicitamente legado, sem alterar status/datas.
        for table in (d, m):
            conn.execute(
                table.update()
                .where(table.c.unidade_id == unit)
                .values(plantao_id=ids[0])
            )
    for name in ("dias_plantao", "dias_marcados_plantao"):
        with op.batch_alter_table(name) as batch:
            batch.alter_column("plantao_id", existing_type=sa.Integer(), nullable=False)
            batch.create_foreign_key(
                f"fk_{name}_plantao_id", "plantao", ["plantao_id"], ["id"]
            )
            batch.create_index(f"ix_{name}_plantao_id", ["plantao_id"])


def downgrade():
    conn = op.get_bind()
    if conn.execute(
        sa.text("SELECT COUNT(*) FROM plantao WHERE legado = 0")
    ).scalar_one():
        raise RuntimeError(
            "Downgrade perderia as escalas e seus vínculos. Restaure um backup anterior."
        )
    for name in ("dias_marcados_plantao", "dias_plantao"):
        with op.batch_alter_table(name) as batch:
            batch.drop_constraint(f"fk_{name}_plantao_id", type_="foreignkey")
            batch.drop_index(f"ix_{name}_plantao_id")
            batch.drop_column("plantao_id")
    for name in ("historico", "cancelado", "legado", "nome"):
        op.drop_column("plantao", name)
