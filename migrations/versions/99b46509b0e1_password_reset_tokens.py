"""password_reset_tokens: tokens de recuperação de senha

Revision ID: 99b46509b0e1
Revises: 3f8c2d61b45a
Create Date: 2026-09-03

Guarda o hash do token enviado por e-mail, o prazo de validade e o momento do
uso. O valor em claro só existe no link enviado ao usuário.
"""

import sqlalchemy as sa
from alembic import op

revision = "99b46509b0e1"
down_revision = "3f8c2d61b45a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expira_em", sa.DateTime(), nullable=False),
        sa.Column("usado_em", sa.DateTime(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["usuario_id"], ["usuarios.id"], name="fk_password_reset_usuario"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_password_reset_token_hash"),
    )
    # A busca por usuario_id (limite de pedidos, invalidação dos anteriores)
    # usa o índice que o MySQL cria junto com a chave estrangeira.


def downgrade() -> None:
    op.drop_table("password_reset_tokens")
