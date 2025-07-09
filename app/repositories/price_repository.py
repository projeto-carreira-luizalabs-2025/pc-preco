from sqlalchemy import Boolean, Column, Integer

from app.integrations.database.sqlalchemy_client import SQLAlchemyClient

from ..models import Price
from .base.sqlalchemy_crud_repository import SQLAlchemyCrudRepository
from .base.sqlalchemy_entity_base import SellerIdSkuPersistableEntityBase


class PriceBase(SellerIdSkuPersistableEntityBase):

    __tablename__ = "pc_preco"

    de = Column(Integer, nullable=False)
    por = Column(Integer, nullable=False)
    alerta_pendente = Column(Boolean, default=False, nullable=False)


class PriceRepository(SQLAlchemyCrudRepository[Price, PriceBase]):

    def __init__(self, sql_client: SQLAlchemyClient):
        """
        Inicializa o repositório de preços com o cliente SQLAlchemy.
        :param sql_client: Instância do cliente SQLAlchemy.
        """
        super().__init__(sql_client=sql_client, model_class=Price, entity_base_class=PriceBase)


__all__ = ["PriceRepository"]
