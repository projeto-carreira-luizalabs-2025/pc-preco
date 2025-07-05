"""add created_at and updated_at to pc_preco_historico

Revision ID: 19750fb7f442
Revises: 6ae8df7fc5eb
Create Date: 2025-07-05 15:09:10.131385

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19750fb7f442'
down_revision: Union[str, None] = '6ae8df7fc5eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pc_preco_historico', sa.Column(
        'created_at',
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False
    ))

    op.add_column('pc_preco_historico', sa.Column(
        'updated_at',
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False
    ))


def downgrade() -> None:
    op.drop_column('pc_preco_historico', 'updated_at')
    op.drop_column('pc_preco_historico', 'created_at')
