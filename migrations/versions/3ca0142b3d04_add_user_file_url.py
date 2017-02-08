"""add user_file_url

Revision ID: 3ca0142b3d04
Revises: 51a3b6570145
Create Date: 2017-02-07 22:07:16.545000

"""

# revision identifiers, used by Alembic.
revision = '3ca0142b3d04'
down_revision = '51a3b6570145'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('gravator_url', sa.String(length=64), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'gravator_url')
    ### end Alembic commands ###