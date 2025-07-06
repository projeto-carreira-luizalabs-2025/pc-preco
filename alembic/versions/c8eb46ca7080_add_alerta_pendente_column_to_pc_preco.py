"""add alerta_pendente column to pc_preco

Revision ID: c8eb46ca7080
Revises: 7b3fef4754f0
Create Date: 2025-07-03 22:15:30.109212

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8eb46ca7080'
down_revision: Union[str, None] = '7b3fef4754f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column('pc_preco', sa.Column('alerta_pendente', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('pc_preco', 'alerta_pendente')
