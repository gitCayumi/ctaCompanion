"""User powers and days

Revision ID: 9d42eefddec8
Revises: a9c8688911e5
Create Date: 2020-06-05 12:22:59.578321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d42eefddec8'
down_revision = 'a9c8688911e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('artifactPower', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('daysPlayed', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('heroPower', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('prismPower', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_user_artifactPower'), 'user', ['artifactPower'], unique=False)
    op.create_index(op.f('ix_user_daysPlayed'), 'user', ['daysPlayed'], unique=False)
    op.create_index(op.f('ix_user_heroPower'), 'user', ['heroPower'], unique=False)
    op.create_index(op.f('ix_user_prismPower'), 'user', ['prismPower'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_prismPower'), table_name='user')
    op.drop_index(op.f('ix_user_heroPower'), table_name='user')
    op.drop_index(op.f('ix_user_daysPlayed'), table_name='user')
    op.drop_index(op.f('ix_user_artifactPower'), table_name='user')
    op.drop_column('user', 'prismPower')
    op.drop_column('user', 'heroPower')
    op.drop_column('user', 'daysPlayed')
    op.drop_column('user', 'artifactPower')
    # ### end Alembic commands ###