from typing import Any, Dict, List, Optional, Callable

from sqlalchemy import Column, Integer

from ..models import Price

from .base.sqlalchemy_crud_repository import SQLAlchemyCrudRepository
from .base.sqlalchemy_entity_base import SellerIdSkuPersistableEntityBase
from app.integrations.database.sqlalchemy_client import SQLAlchemyClient


class PriceBase(SellerIdSkuPersistableEntityBase):
    __tablename__ = "pc_preco"

    de = Column(Integer, nullable=False)
    por = Column(Integer, nullable=False)


class PriceRepository(SQLAlchemyCrudRepository[Price, PriceBase]):
    def __init__(self, sql_client: SQLAlchemyClient):
        """
        Inicializa o repositório de preços com o cliente SQLAlchemy.
        :param sql_client: Instância do cliente SQLAlchemy.
        """
        super().__init__(sql_client=sql_client, model_class=Price, entity_base_class=PriceBase)

    async def find_by_seller_id_and_sku(self, seller_id: str, sku: str) -> Optional[Dict[str, Any]]:
        """
        Busca um preço pela junção de seller_id + sku

        :param seller_id: ID do vendedor.
        :param sku: Código do produto.
        :return: Dicionário do price encontrado.
        """

        result = await super().find_by_seller_id_and_sku(seller_id, sku)
        result = result.model_dump() if result else None

        return result

    async def update_by_seller_id_and_sku(self, seller_id: str, sku: str, price_update: Price) -> Dict[str, Any]:
        """
        Atualiza um preço na memória pela junção de seller_id + sku.

        :param seller_id: ID do vendedor.
        :param sku: Código do produto.
        :param price_update: Dicionário com os dados a serem atualizados.
        :return: True se encontrado, False caso contrário.
        """
        result = await super().update_by_seller_id_and_sku(seller_id, sku, price_update)
        return result

    async def delete_by_seller_id_and_sku(self, seller_id: str, sku: str) -> None:
        """
        Remove um preco da memória com base no ID.

        :param seller_id: ID do vendedor.
        :param sku: Código do produto.
        :return: None
        """
        deleted = await super().delete_by_seller_id_and_sku(seller_id, sku)
        return deleted


__all__ = ["PriceRepository"]
