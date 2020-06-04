"""added runedValues

Revision ID: a9c8688911e5
Revises: e41645aad309
Create Date: 2020-06-03 20:41:35.369379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9c8688911e5'
down_revision = 'e41645aad309'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hero', sa.Column('runedAps', sa.Integer(), nullable=True))
    op.add_column('hero', sa.Column('runedAtk', sa.Integer(), nullable=True))
    op.add_column('hero', sa.Column('runedCrit', sa.Integer(), nullable=True))
    op.add_column('hero', sa.Column('runedCritDmg', sa.Integer(), nullable=True))
    op.add_column('hero', sa.Column('runedDef', sa.Integer(), nullable=True))
    op.add_column('hero', sa.Column('runedHp', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_hero_runedAps'), 'hero', ['runedAps'], unique=False)
    op.create_index(op.f('ix_hero_runedAtk'), 'hero', ['runedAtk'], unique=False)
    op.create_index(op.f('ix_hero_runedCrit'), 'hero', ['runedCrit'], unique=False)
    op.create_index(op.f('ix_hero_runedCritDmg'), 'hero', ['runedCritDmg'], unique=False)
    op.create_index(op.f('ix_hero_runedDef'), 'hero', ['runedDef'], unique=False)
    op.create_index(op.f('ix_hero_runedHp'), 'hero', ['runedHp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_hero_runedHp'), table_name='hero')
    op.drop_index(op.f('ix_hero_runedDef'), table_name='hero')
    op.drop_index(op.f('ix_hero_runedCritDmg'), table_name='hero')
    op.drop_index(op.f('ix_hero_runedCrit'), table_name='hero')
    op.drop_index(op.f('ix_hero_runedAtk'), table_name='hero')
    op.drop_index(op.f('ix_hero_runedAps'), table_name='hero')
    op.drop_column('hero', 'runedHp')
    op.drop_column('hero', 'runedDef')
    op.drop_column('hero', 'runedCritDmg')
    op.drop_column('hero', 'runedCrit')
    op.drop_column('hero', 'runedAtk')
    op.drop_column('hero', 'runedAps')
    # ### end Alembic commands ###