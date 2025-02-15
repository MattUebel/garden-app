"""add_harvests_table

Revision ID: 004
Revises: 003
Create Date: 2024-01-09

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('harvests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plant_id', sa.Integer(), nullable=False),
        sa.Column('harvest_date', sa.DateTime(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_harvests_id'), 'harvests', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_harvests_id'), table_name='harvests')
    op.drop_table('harvests')