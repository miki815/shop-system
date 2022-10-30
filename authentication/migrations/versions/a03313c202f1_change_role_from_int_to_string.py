"""change role from int to string

Revision ID: a03313c202f1
Revises: 6a7a1344243c
Create Date: 2022-07-13 03:36:49.218108

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a03313c202f1'
down_revision = '6a7a1344243c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'role',
               existing_type=mysql.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'role',
               existing_type=mysql.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
