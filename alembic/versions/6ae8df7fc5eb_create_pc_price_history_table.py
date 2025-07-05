"""create_pc_price_history_table

Revision ID: 6ae8df7fc5eb
Revises: c591a263c682
Create Date: 2025-07-04 19:08:20.998160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ae8df7fc5eb'
down_revision: Union[str, None] = 'c591a263c682'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'pc_preco_historico',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('sku', sa.String(), nullable=False),
        sa.Column('de', sa.Integer(), nullable=False),
        sa.Column('por', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.String(), nullable=False),
        sa.Column('registered_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    
def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('pc_preco_historico')