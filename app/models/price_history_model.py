import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.integrations.database.sqlalchemy_client import Base


class PriceHistory(Base):
    __tablename__ = "pc_price_history"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    sku: Mapped[str] = mapped_column(sa.String, nullable=False)
    seller_id: Mapped[str] = mapped_column(sa.String, nullable=False)
    de: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    por: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    registered_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False
    )
