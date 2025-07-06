"""merge heads

Revision ID: 2f0cdc100f14
Revises: 67cfd1fa2e74, c8eb46ca7080
Create Date: 2025-07-06 14:39:52.728543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f0cdc100f14'
down_revision: Union[str, None] = ('67cfd1fa2e74', 'c8eb46ca7080')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
