from sqlalchemy import Column, Integer

from app.models.price_history_model import PriceHistory
from .base.sqlalchemy_crud_repository import SQLAlchemyCrudRepository
from .base.sqlalchemy_entity_base import SellerIdSkuPersistableEntityBase
from app.integrations.database.sqlalchemy_client import SQLAlchemyClient

class PriceHistoryBase(SellerIdSkuPersistableEntityBase):
    __tablename__ = "pc_preco_historico"

    de = Column(Integer, nullable=False)
    por = Column(Integer, nullable=False)

class PriceHistoryRepository(SQLAlchemyCrudRepository[PriceHistory, PriceHistoryBase]):
    def __init__(self, sql_client: SQLAlchemyClient):
        super().__init__(
            sql_client=sql_client,
            model_class=PriceHistory,
            entity_base_class=PriceHistoryBase,
        )

__all__ = ["PriceHistoryRepository"]
