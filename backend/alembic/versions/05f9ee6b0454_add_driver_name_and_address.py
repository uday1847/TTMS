"""add_driver_name_and_address

Revision ID: 05f9ee6b0454
Revises: 0001
Create Date: 2026-07-13 14:09:23.204554

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05f9ee6b0454'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('drivers', sa.Column('name', sa.String(length=100), nullable=False, server_default=""))
    op.add_column('drivers', sa.Column('address', sa.String(length=500), nullable=True))
    op.create_index(op.f('ix_drivers_user_id'), 'drivers', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_drivers_user_id'), table_name='drivers')
    op.drop_column('drivers', 'address')
    op.drop_column('drivers', 'name')
