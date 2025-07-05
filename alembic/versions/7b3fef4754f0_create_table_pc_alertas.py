"""create table pc_alertas

Revision ID: 7b3fef4754f0
Revises: c591a263c682
Create Date: 2025-07-03 22:06:27.731125

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b3fef4754f0'
down_revision: Union[str, None] = 'c591a263c682'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "pc_alertas",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("seller_id", sa.String, nullable=False),
        sa.Column("sku", sa.String, nullable=False),
        sa.Column("mensagem", sa.String, nullable=False),
        sa.Column("status", sa.String, nullable=False, default="pendente"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("pc_alertas")
