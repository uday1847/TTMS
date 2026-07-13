"""add_driver_phone_unique_index

Revision ID: 630fcd950c9a
Revises: 05f9ee6b0454
Create Date: 2026-07-13 14:21:02.580618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '630fcd950c9a'
down_revision: Union[str, Sequence[str], None] = '05f9ee6b0454'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index('uq_drivers_contact_phone', 'drivers', ['contact_phone'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_drivers_contact_phone', table_name='drivers')
