"""return

Revision ID: a48dae201d0a
Revises: 3516bd56b5c7
Create Date: 2017-02-11 13:05:55.639000

"""

# revision identifiers, used by Alembic.
revision = 'a48dae201d0a'
down_revision = '3516bd56b5c7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    # op.drop_column('posts', 'test')
    ### end Alembic commands ###
	pass


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    # op.add_column('posts', sa.Column('test', sa.VARCHAR(length=64), nullable=True))
    ### end Alembic commands ###
	pass
