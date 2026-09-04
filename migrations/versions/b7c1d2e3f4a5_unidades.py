"""unidades: multiunidade (Belo Horizonte e Nova Lima)

Revision ID: b7c1d2e3f4a5
Revises: 99b46509b0e1
Create Date: 2026-09-04

Cria a tabela `unidades` com as duas unidades da DAJ, o vínculo
`usuarios_unidades` (todo usuário existente passa a pertencer a Belo
Horizonte) e a coluna `unidade_id` nas onze tabelas raiz. Os registros
herdados da 2.0 são todos de Belo Horizonte, a unidade 1 — o mesmo
`UNIDADE_PADRAO_ID` de `gestaolegal/database/tables.py`.

A coluna entra nullable, é preenchida com 1 e só então vira NOT NULL: numa
base com dados um `add_column` NOT NULL sem default falharia.
"""

from datetime import datetime

import sqlalchemy as sa
from alembic import op

revision = "b7c1d2e3f4a5"
down_revision = "99b46509b0e1"
branch_labels = None
depends_on = None

UNIDADE_PADRAO_ID = 1

# Tabelas raiz que ganham `unidade_id`. Entidades filhas (arquivos, processos,
# históricos, assistidos) não têm coluna própria: a unidade vem do pai.
TABELAS_RAIZ = (
    "atendidos",
    "orientacao_juridica",
    "casos",
    "eventos",
    "assistencias_judiciarias",
    "lembretes",
    "fila_atendimentos",
    "dias_plantao",
    "plantao",
    "dias_marcados_plantao",
    "registro_entrada",
)


def upgrade() -> None:
    unidades = op.create_table(
        "unidades",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(60), nullable=False),
        sa.Column("sigla", sa.String(10), nullable=False),
        sa.Column("ativa", sa.Boolean(), nullable=False),
        sa.Column("criado", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome", name="uq_unidades_nome"),
        sa.UniqueConstraint("sigla", name="uq_unidades_sigla"),
    )
    agora = datetime.now()
    op.bulk_insert(
        unidades,
        [
            {
                "id": 1,
                "nome": "Belo Horizonte",
                "sigla": "BH",
                "ativa": True,
                "criado": agora,
            },
            {
                "id": 2,
                "nome": "Nova Lima",
                "sigla": "NL",
                "ativa": True,
                "criado": agora,
            },
        ],
    )

    op.create_table(
        "usuarios_unidades",
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("unidade_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["usuario_id"], ["usuarios.id"], name="fk_usuarios_unidades_usuario"
        ),
        sa.ForeignKeyConstraint(
            ["unidade_id"], ["unidades.id"], name="fk_usuarios_unidades_unidade"
        ),
        sa.PrimaryKeyConstraint("usuario_id", "unidade_id"),
    )
    # Todo usuário herdado é de Belo Horizonte; o vínculo com Nova Lima é
    # concedido depois, pela tela de usuários.
    op.execute(
        "INSERT INTO usuarios_unidades (usuario_id, unidade_id) "
        f"SELECT id, {UNIDADE_PADRAO_ID} FROM usuarios"
    )

    for tabela in TABELAS_RAIZ:
        op.add_column(tabela, sa.Column("unidade_id", sa.Integer(), nullable=True))
        op.execute(f"UPDATE {tabela} SET unidade_id = {UNIDADE_PADRAO_ID}")
        op.alter_column(
            tabela,
            "unidade_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        op.create_index(f"ix_{tabela}_unidade_id", tabela, ["unidade_id"])
        op.create_foreign_key(
            f"fk_{tabela}_unidade", tabela, "unidades", ["unidade_id"], ["id"]
        )


def downgrade() -> None:
    for tabela in reversed(TABELAS_RAIZ):
        op.drop_constraint(f"fk_{tabela}_unidade", tabela, type_="foreignkey")
        op.drop_index(f"ix_{tabela}_unidade_id", table_name=tabela)
        op.drop_column(tabela, "unidade_id")

    op.drop_table("usuarios_unidades")
    op.drop_table("unidades")
