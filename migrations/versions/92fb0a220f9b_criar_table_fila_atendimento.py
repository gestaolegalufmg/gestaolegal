"""criar table fila atendimento

Revision ID: 92fb0a220f9b
Revises: 3b49077db314
Create Date: 2023-11-14 18:53:38.927379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92fb0a220f9b'
down_revision = '3b49077db314'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'fila_atendimentos',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('psicologia', sa.Integer, nullable=False),
        sa.Column('id_atendido', sa.Integer, nullable=False),
        sa.Column('prioridade', sa.Integer, nullable=False),
        sa.Column('senha', sa.String(length=10), nullable=False),
        sa.Column('data_criacao', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(['id_atendido'], ['atendidos.id'])
    )


def downgrade():
    op.drop_table('fila_atendimentos')
