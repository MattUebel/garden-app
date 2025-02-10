"""create base tables

Revision ID: 000
Revises: 
Create Date: 2024-02-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '000'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create garden_beds table
    op.create_table(
        'garden_beds',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String()),
        sa.Column('dimensions', sa.String()),
        sa.Column('notes', sa.String(), nullable=True),
    )

    # Create plants table
    op.create_table(
        'plants',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String()),
        sa.Column('variety', sa.String(), nullable=True),
        sa.Column('planting_date', sa.DateTime()),
        sa.Column('bed_id', sa.Integer(), sa.ForeignKey('garden_beds.id')),
        sa.Column('status', sa.String()),
        sa.Column('season', sa.String()),
        sa.Column('quantity', sa.Integer(), default=1),
        sa.Column('expected_harvest_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
    )

def downgrade() -> None:
    op.drop_table('plants')
    op.drop_table('garden_beds')