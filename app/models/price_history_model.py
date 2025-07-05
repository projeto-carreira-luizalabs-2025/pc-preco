import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.integrations.database.sqlalchemy_client import Base
from app.models.base import SellerSkuIntHistoryPersistableEntity


class PriceHistory(SellerSkuIntHistoryPersistableEntity):
    de: int
    por: int