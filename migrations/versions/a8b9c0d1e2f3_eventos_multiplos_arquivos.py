"""Anexos de eventos 1:N, preservando referências e IDs legados.

Não move arquivos físicos. O campo antigo fica vazio após a transferência
para arquivosEvento e permanece na estrutura para permitir reversão segura.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "a8b9c0d1e2f3"
down_revision = "f7a8b9c0d1e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    if not sa.inspect(conn).has_table("arquivosEvento"):
        op.create_table(
            "arquivosEvento",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("id_evento", sa.Integer(), sa.ForeignKey("eventos.id", ondelete="CASCADE")),
            sa.Column("id_caso", sa.Integer(), sa.ForeignKey("casos.id", ondelete="CASCADE")),
            sa.Column("link_arquivo", sa.String(300)),
        )
    invalidos = conn.execute(sa.text(
        "SELECT COUNT(*) FROM arquivosEvento a LEFT JOIN eventos e ON e.id=a.id_evento "
        "WHERE e.id IS NULL OR a.id_caso IS NULL OR a.id_caso<>e.id_caso"
    )).scalar_one()
    if invalidos:
        raise RuntimeError("Anexos legados com evento/caso inválido: corrija os vínculos antes de migrar.")
    op.alter_column(
        "arquivosEvento", "link_arquivo", existing_type=sa.String(300),
        type_=mysql.VARCHAR(300, charset="utf8mb4", collation="utf8mb4_0900_ai_ci"),
        existing_nullable=True,
    )
    eventos = sa.Table("eventos", sa.MetaData(), autoload_with=conn)
    anexos = sa.Table("arquivosEvento", sa.MetaData(), autoload_with=conn)
    for row in conn.execute(sa.select(eventos.c.id, eventos.c.id_caso, eventos.c.arquivo)).mappings():
        if not row["arquivo"]:
            continue
        refs = conn.execute(sa.select(anexos.c.link_arquivo).where(
            anexos.c.id_evento == row["id"])).scalars().all()
        # Igualdade exata: a collation do banco não distingue todos os nomes de arquivo.
        if row["arquivo"] not in refs:
            conn.execute(anexos.insert().values(
                id_evento=row["id"], id_caso=row["id_caso"], link_arquivo=row["arquivo"]))
        conn.execute(eventos.update().where(eventos.c.id == row["id"]).values(arquivo=None))


def downgrade() -> None:
    conn = op.get_bind()
    multiplos = conn.execute(sa.text(
        "SELECT id_evento FROM arquivosEvento GROUP BY id_evento HAVING COUNT(*)>1 LIMIT 1"
    )).first()
    if multiplos:
        raise RuntimeError("Downgrade abortado: há eventos com múltiplos anexos; o campo único perderia dados.")
    conn.execute(sa.text(
        "UPDATE eventos e JOIN arquivosEvento a ON a.id_evento=e.id "
        "SET e.arquivo=a.link_arquivo"
    ))
    # Conserva a tabela: ela também existia antes desta revisão nos dumps.
