"""Add collections.

Revision ID: 294cd1b0969a
Revises: 274f2cdaa8db
Create Date: 2013-09-14 06:41:00.240580

"""

# revision identifiers, used by Alembic.
revision = '294cd1b0969a'
down_revision = '274f2cdaa8db'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('collections',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'messagepart', sa.Column('collection_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'messagepart', 'collection_id')
    op.drop_table('collections')
    ### end Alembic commands ###
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
