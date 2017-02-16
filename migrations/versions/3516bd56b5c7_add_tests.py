"""add tests

Revision ID: 3516bd56b5c7
Revises: b6b9a5e6d7a1
Create Date: 2017-02-11 13:03:29.487000

"""

# revision identifiers, used by Alembic.
revision = '3516bd56b5c7'
down_revision = 'b6b9a5e6d7a1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tags')
    op.add_column('posts', sa.Column('test', sa.String(length=64), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'test')
    op.create_table('tags',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('tagsname', sa.VARCHAR(length=64), nullable=True),
    sa.Column('post_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], [u'posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###