"""empty message

Revision ID: 571666e276aa
Revises: 3804674a246f
Create Date: 2023-02-15 17:11:00.215574

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '571666e276aa'
down_revision = '3804674a246f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_column('total_amount_received')
        batch_op.drop_column('total_amount_payable')

    with op.batch_alter_table('sales_order', schema=None) as batch_op:
        batch_op.alter_column('total_paid',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.Float(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_order', schema=None) as batch_op:
        batch_op.alter_column('total_paid',
               existing_type=sa.Float(),
               type_=sa.VARCHAR(length=100),
               existing_nullable=True)

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total_amount_payable', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('total_amount_received', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
