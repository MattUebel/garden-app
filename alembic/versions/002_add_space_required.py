"""add space required column

Revision ID: 002_add_space_required
Revises: 001
Create Date: 2024-01-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_space_required'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('plants', sa.Column('space_required', sa.Integer, nullable=True))


def downgrade() -> None:
    op.drop_column('plants', 'space_required')