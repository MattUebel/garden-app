"""add year column

Revision ID: 001
Revises: 000
Create Date: 2024-02-10

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '001'
down_revision = '000'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add year column to plants table
    op.add_column('plants', sa.Column('year', sa.Integer(), nullable=True))
    # Set default year for existing plants to current year
    op.execute(f"UPDATE plants SET year = {datetime.now().year} WHERE year IS NULL")

def downgrade() -> None:
    op.drop_column('plants', 'year')