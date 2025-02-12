"""remove_season_field

Revision ID: 003
Revises: 002_add_space_required
Create Date: 2024-01-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002_add_space_required'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the season column from plants table
    op.drop_column('plants', 'season')


def downgrade() -> None:
    # Add back the season column if we need to downgrade
    op.add_column('plants', sa.Column('season', sa.String(), nullable=True))