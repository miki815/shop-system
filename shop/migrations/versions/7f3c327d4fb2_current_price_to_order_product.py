"""current price to order product

Revision ID: 7f3c327d4fb2
Revises: b502eb116090
Create Date: 2022-07-14 15:35:48.904723

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f3c327d4fb2'
down_revision = 'b502eb116090'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orderproduct', sa.Column('price', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orderproduct', 'price')
    # ### end Alembic commands ###
