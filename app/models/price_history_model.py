import sqlalchemy as sa
from datetime import datetime
from pydantic import Field
from app.common.datetime import utcnow

from app.integrations.database.sqlalchemy_client import Base
from app.models.base import IntModel, SellerSkuEntity, CreatedByMixin, UpdatedByMixin


class PriceHistory(IntModel, SellerSkuEntity, CreatedByMixin, UpdatedByMixin):
    de: int
    por: int
    registered_at: datetime | None = Field(default_factory=utcnow, description="Data e hora de registro")
