"""Add latitude and longitude to User model

Revision ID: a4b39f323868
Revises: 
Create Date: 2024-09-15 19:57:05.841895

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4b39f323868'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('users', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('longitude', sa.Float(), nullable=True))


def downgrade():
    op.drop_column('users', 'latitude')
    op.drop_column('users', 'longitude')
