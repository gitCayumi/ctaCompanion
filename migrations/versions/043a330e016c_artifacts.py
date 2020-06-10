"""Artifacts

Revision ID: 043a330e016c
Revises: 9d42eefddec8
Create Date: 2020-06-07 22:16:49.296447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '043a330e016c'
down_revision = '9d42eefddec8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('art_base',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('star', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('atk', sa.Integer(), nullable=True),
    sa.Column('atkLevel', sa.Integer(), nullable=True),
    sa.Column('critDmg', sa.Integer(), nullable=True),
    sa.Column('critDmgLevel', sa.Integer(), nullable=True),
    sa.Column('element', sa.String(length=16), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_art_base_atk'), 'art_base', ['atk'], unique=False)
    op.create_index(op.f('ix_art_base_atkLevel'), 'art_base', ['atkLevel'], unique=False)
    op.create_index(op.f('ix_art_base_critDmg'), 'art_base', ['critDmg'], unique=False)
    op.create_index(op.f('ix_art_base_critDmgLevel'), 'art_base', ['critDmgLevel'], unique=False)
    op.create_index(op.f('ix_art_base_element'), 'art_base', ['element'], unique=False)
    op.create_index(op.f('ix_art_base_name'), 'art_base', ['name'], unique=False)
    op.create_index(op.f('ix_art_base_star'), 'art_base', ['star'], unique=False)
    op.create_table('artifact',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('artbase_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['artbase_id'], ['art_base.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artifact_level'), 'artifact', ['level'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_artifact_level'), table_name='artifact')
    op.drop_table('artifact')
    op.drop_index(op.f('ix_art_base_star'), table_name='art_base')
    op.drop_index(op.f('ix_art_base_name'), table_name='art_base')
    op.drop_index(op.f('ix_art_base_element'), table_name='art_base')
    op.drop_index(op.f('ix_art_base_critDmgLevel'), table_name='art_base')
    op.drop_index(op.f('ix_art_base_critDmg'), table_name='art_base')
    op.drop_index(op.f('ix_art_base_atkLevel'), table_name='art_base')
    op.drop_index(op.f('ix_art_base_atk'), table_name='art_base')
    op.drop_table('art_base')
    # ### end Alembic commands ###