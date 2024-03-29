"""empty message

Revision ID: fdc2b6df65b7
Revises: 9e8278c1c8cd
Create Date: 2023-01-26 18:03:15.925678

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdc2b6df65b7'
down_revision = '9e8278c1c8cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment_voucher', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reference_no', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment_voucher', schema=None) as batch_op:
        batch_op.drop_column('reference_no')

    # ### end Alembic commands ###
