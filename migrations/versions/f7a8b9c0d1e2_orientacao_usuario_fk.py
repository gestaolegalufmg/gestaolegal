"""Garante a referência do autor da orientação, preservando autoria desconhecida."""

import sqlalchemy as sa
from alembic import op

revision = "f7a8b9c0d1e2"
down_revision = "e6f7a8b9c0d1"
branch_labels = None
depends_on = None

FK_NAME = "fk_orientacao_juridica_usuario"


def upgrade() -> None:
    conn = op.get_bind()
    invalidos = conn.execute(sa.text(
        "SELECT COUNT(*) FROM orientacao_juridica o "
        "LEFT JOIN usuarios u ON u.id = o.id_usuario "
        "WHERE o.id_usuario IS NOT NULL AND u.id IS NULL"
    )).scalar_one()
    if invalidos:
        raise RuntimeError(
            f"Migration abortada: {invalidos} orientação(ões) com usuário "
            "inexistente. Corrija as referências antes de criar a chave estrangeira."
        )
    for fk in sa.inspect(conn).get_foreign_keys("orientacao_juridica"):
        if "id_usuario" not in fk["constrained_columns"]:
            continue
        if (
            fk["constrained_columns"] == ["id_usuario"]
            and fk["referred_table"] == "usuarios"
            and fk["referred_columns"] == ["id"]
            and fk.get("referred_schema") in (None, conn.dialect.default_schema_name)
        ):
            return
        raise RuntimeError("Chave estrangeira inesperada em orientacao_juridica.id_usuario.")
    op.create_foreign_key(
        FK_NAME, "orientacao_juridica", "usuarios", ["id_usuario"], ["id"],
    )


def downgrade() -> None:
    # Não remove a FK legada de BH: só a criada por esta revisão.
    for fk in sa.inspect(op.get_bind()).get_foreign_keys("orientacao_juridica"):
        if fk["name"] == FK_NAME:
            op.drop_constraint(FK_NAME, "orientacao_juridica", type_="foreignkey")
            return
