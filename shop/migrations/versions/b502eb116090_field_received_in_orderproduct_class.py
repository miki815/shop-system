"""Field received in orderproduct class

Revision ID: b502eb116090
Revises: a0450540dbd4
Create Date: 2022-07-12 23:12:43.495834

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b502eb116090'
down_revision = 'a0450540dbd4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orderproduct', sa.Column('received', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orderproduct', 'received')
    # ### end Alembic commands ###
