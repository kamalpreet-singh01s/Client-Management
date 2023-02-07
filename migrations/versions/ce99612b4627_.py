"""empty message

Revision ID: ce99612b4627
Revises: 84cb5f348aa3
Create Date: 2023-01-25 15:20:31.511582

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce99612b4627'
down_revision = '84cb5f348aa3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('paymentvoucher')
    with op.batch_alter_table('payment_voucher', schema=None) as batch_op:
        batch_op.add_column(sa.Column('amount', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.Enum('Draft', 'Approved', 'Cancelled', name='paymentstatus'), nullable=True))
        batch_op.alter_column('payment_date',
               existing_type=sa.DATE(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('approval_date',
               existing_type=sa.DATE(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.alter_column('bill',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.create_foreign_key(None, 'records', ['bill'], ['bill'])
        batch_op.drop_column('bill_date')
        batch_op.drop_column('amount_received')
        batch_op.drop_column('dop')

    with op.batch_alter_table('records', schema=None) as batch_op:
        batch_op.alter_column('bill',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('records', schema=None) as batch_op:
        batch_op.alter_column('bill',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)

    with op.batch_alter_table('payment_voucher', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dop', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('amount_received', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('bill_date', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('bill',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('approval_date',
               existing_type=sa.String(),
               type_=sa.DATE(),
               existing_nullable=True)
        batch_op.alter_column('payment_date',
               existing_type=sa.String(),
               type_=sa.DATE(),
               existing_nullable=True)
        batch_op.drop_column('status')
        batch_op.drop_column('amount')

    op.create_table('paymentvoucher',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('payment_date', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('approval_date', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('dop', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('bill', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('bill_date', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='paymentvoucher_pkey')
    )
    # ### end Alembic commands ###