"""Add created_by and updated_by to pc_preco_historico

Revision ID: 67cfd1fa2e74
Revises: 19750fb7f442
Create Date: 2025-07-05 22:00:58.710068
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '67cfd1fa2e74'
down_revision: Union[str, None] = '19750fb7f442'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # Adiciona as colunas created_by e updated_by à tabela pc_preco_historico
    op.add_column(
        'pc_preco_historico',
        sa.Column('created_by', postgresql.JSONB, nullable=False, server_default='{}')
    )
    op.add_column(
        'pc_preco_historico',
        sa.Column('updated_by', postgresql.JSONB, nullable=False, server_default='{}')
    )

def downgrade() -> None:
    """Downgrade schema."""
    # Remove as colunas created_by e updated_by
    op.drop_column('pc_preco_historico', 'created_by')
    op.drop_column('pc_preco_historico', 'updated_by')