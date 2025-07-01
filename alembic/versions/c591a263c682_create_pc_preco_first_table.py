"""create 'pc-preco' first table

Revision ID: c591a263c682
Revises:
Create Date: 2025-06-03 19:08:33.833701

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.repositories.price_repository import PriceBase

# revision identifiers, used by Alembic.
revision: str = 'c591a263c682'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'pc_preco',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('sku', sa.String(), nullable=False),
        sa.Column('de', sa.Integer(), nullable=False),
        sa.Column('por', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.Column('created_by', sa.JSON(), nullable=False),
        sa.Column('updated_by', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index("idx_anything_sellerid_sku", PriceBase.__tablename__, ["seller_id", "sku"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table(PriceBase.__tablename__)
