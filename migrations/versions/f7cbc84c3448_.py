"""empty message

Revision ID: f7cbc84c3448
Revises: 8a29081e6780
Create Date: 2023-02-15 13:54:21.881949

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f7cbc84c3448'
down_revision = '8a29081e6780'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_order', schema=None) as batch_op:
        batch_op.drop_column('total_paid')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total_paid', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
