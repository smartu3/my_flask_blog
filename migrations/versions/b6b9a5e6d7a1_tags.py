"""tags

Revision ID: b6b9a5e6d7a1
Revises: dbcb56baa797
Create Date: 2017-02-10 17:00:35.051000

"""

# revision identifiers, used by Alembic.
revision = 'b6b9a5e6d7a1'
down_revision = 'dbcb56baa797'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    # op.create_table('tags',
    # sa.Column('id', sa.Integer(), nullable=False),
    # sa.Column('tagsname', sa.String(length=64), nullable=True),
    # sa.Column('post_id', sa.Integer(), nullable=True),
    # sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    # sa.PrimaryKeyConstraint('id')
    # )
    # op.drop_column(u'posts', 'tags')
    ### end Alembic commands ###
    pass


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    # op.add_column(u'posts', sa.Column('tags', sa.VARCHAR(length=64), nullable=True))
    # op.drop_table('tags')
    ### end Alembic commands ###
    pass