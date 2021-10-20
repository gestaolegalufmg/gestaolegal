"""empty message

Revision ID: d9bd50e346e4
Revises: 6bf40f817493
Create Date: 2021-10-20 15:00:46.097858

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd9bd50e346e4'
down_revision = '6bf40f817493'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('enderecos', 'cep',
               existing_type=mysql.VARCHAR(charset='latin1', collation='latin1_general_ci', length=10),
               type_=sa.String(length=9, collation='latin1_general_ci'),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('enderecos', 'cep',
               existing_type=sa.String(length=9, collation='latin1_general_ci'),
               type_=mysql.VARCHAR(charset='latin1', collation='latin1_general_ci', length=10),
               existing_nullable=False)
        # ### end Alembic commands ###
