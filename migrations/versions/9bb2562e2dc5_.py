"""empty message

Revision ID: 9bb2562e2dc5
Revises: 74f89c02a632
Create Date: 2019-09-18 23:32:41.067894

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9bb2562e2dc5'
down_revision = '74f89c02a632'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('good', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'good')
    # ### end Alembic commands ###
