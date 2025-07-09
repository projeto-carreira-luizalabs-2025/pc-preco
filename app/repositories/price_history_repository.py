from sqlalchemy import Column, Date, Integer

from app.integrations.database.sqlalchemy_client import SQLAlchemyClient
from app.models.price_history_model import PriceHistory

from .base.sqlalchemy_crud_repository import SQLAlchemyCrudRepository
from .base.sqlalchemy_entity_base import CreatedByMixin, IdEntityBase, SellerIdMixin, SkuMixin, UpdatedByMixin


class PriceHistoryBase(IdEntityBase, CreatedByMixin, UpdatedByMixin, SellerIdMixin, SkuMixin):
    __tablename__ = "pc_preco_historico"

    de = Column(Integer, nullable=False)
    por = Column(Integer, nullable=False)
    registered_at = Column(Date, nullable=False)


class PriceHistoryRepository(SQLAlchemyCrudRepository[PriceHistory, PriceHistoryBase]):

    def __init__(self, sql_client: SQLAlchemyClient):
        super().__init__(
            sql_client=sql_client,
            model_class=PriceHistory,
            entity_base_class=PriceHistoryBase,
        )


__all__ = ["PriceHistoryRepository"]
