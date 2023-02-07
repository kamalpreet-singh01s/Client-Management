"""empty message

Revision ID: ff06c0074635
Revises: 713116eb0487
Create Date: 2023-02-02 16:49:16.946603

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ff06c0074635'
down_revision = '713116eb0487'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_column('gst')
        batch_op.drop_column('final_deal')

    with op.batch_alter_table('sales_order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('final_deal', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('gst', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_order', schema=None) as batch_op:
        batch_op.drop_column('gst')
        batch_op.drop_column('final_deal')

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('final_deal', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('gst', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))

    # ### end Alembic commands ###