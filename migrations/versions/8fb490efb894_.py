"""empty message

Revision ID: 8fb490efb894
Revises: b02c2dd369a4
Create Date: 2020-06-15 20:33:31.609050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8fb490efb894'
down_revision = 'b02c2dd369a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('boss_base',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('nameSafe', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_boss_base_name'), 'boss_base', ['name'], unique=True)
    op.create_index(op.f('ix_boss_base_nameSafe'), 'boss_base', ['nameSafe'], unique=True)
    op.create_table('bossteam',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hero', sa.String(length=16), nullable=True),
    sa.Column('damage', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('bossbase_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['bossbase_id'], ['boss_base.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bossteam_damage'), 'bossteam', ['damage'], unique=False)
    op.create_index(op.f('ix_bossteam_hero'), 'bossteam', ['hero'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_bossteam_hero'), table_name='bossteam')
    op.drop_index(op.f('ix_bossteam_damage'), table_name='bossteam')
    op.drop_table('bossteam')
    op.drop_index(op.f('ix_boss_base_nameSafe'), table_name='boss_base')
    op.drop_index(op.f('ix_boss_base_name'), table_name='boss_base')
    op.drop_table('boss_base')
    # ### end Alembic commands ###