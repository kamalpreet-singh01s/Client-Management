"""removed pen_rec column from records table

Revision ID: fd12d70d45d7
Revises: c9d5556b33c5
Create Date: 2022-10-07 21:20:03.565261

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd12d70d45d7'
down_revision = 'c9d5556b33c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('records', schema=None) as batch_op:
        batch_op.drop_column('payment_rec_date')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_rec_date', sa.VARCHAR(length=100), nullable=True))

    # ### end Alembic commands ###
