from typing import Any, Dict, List, Optional, Callable

from sqlalchemy import Column, Integer

from ..models import Price

from .base.sqlalchemy_crud_repository import SQLAlchemyCrudRepository
from .base.sqlalchemy_entity_base import SellerIdSkuPersistableEntityBase
from app.integrations.database.sqlalchemy_client import SQLAlchemyClient


class PriceBase(SellerIdSkuPersistableEntityBase):
    __tablename__ = "pc_preco"

    value = Column(Integer, nullable=False)


class PriceRepository(SQLAlchemyCrudRepository[Price, PriceBase]):
    def __init__(self, sql_client: SQLAlchemyClient):
        """
        Inicializa o repositório de preços com o cliente SQLAlchemy.
        :param sql_client: Instância do cliente SQLAlchemy.
        """
        super().__init__(sql_client=sql_client, model_class=Price, entity_base_class=PriceBase)

    def _can_filter(self, data: Dict[str, Any], filters: Dict[str, Any] | None) -> bool:
        """
        Verifica se o dicionário de dados atende aos filtros fornecidos.

        :param data: Dicionário representando um objeto Price.
        :param filters: Dicionário de filtros a serem aplicados.
        :return: True se os dados atenderem aos filtros, False caso contrário.
        """
        if not filters:
            return True

        def is_valid_number(value: Any) -> bool:
            return isinstance(value, (int, float))

        # Filtros de comparação para preços
        comparisons: Dict[str, tuple[str, Callable[[float, float], bool]]] = {
            "preco_de_less_than": ("de", lambda x, y: x < y),
            "preco_de_greater_than": ("de", lambda x, y: x > y),
            "preco_por_less_than": ("por", lambda x, y: x < y),
            "preco_por_greater_than": ("por", lambda x, y: x > y),
        }

        # Verifica se todos os filtros de comparação são válidos
        for filter_key, (data_key, comparator) in comparisons.items():
            if filter_key in filters:
                value = data.get(data_key)
                if not is_valid_number(value) or not comparator(value, filters[filter_key]):
                    return False

        # Filtro sku (busca exata)
        if "sku" in filters and data.get("sku") != filters["sku"]:
            return False

        # Se passou por todos os filtros aplicáveis, o item é válido
        return True

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

    async def exists_by_seller_id_and_sku(self, seller_id: str, sku: str) -> bool:
        """
        Verifica se existe um preço para o seller_id e sku informados.

        :param seller_id: ID do vendedor.
        :param sku: Código do produto.
        :return: True se encontrado, False caso contrário.
        """
        return any(price['seller_id'] == seller_id and price['sku'] == sku for price in self.memory)

    async def update_by_seller_id_and_sku(self, seller_id: str, sku: str, price_update: Price) -> Dict[str, Any]:
        """
        Atualiza um preço na memória pela junção de seller_id + sku.

        :param seller_id: ID do vendedor.
        :param sku: Código do produto.
        :param price_update: Dicionário com os dados a serem atualizados.
        :return: True se encontrado, False caso contrário.
        """
        for i, price in enumerate(self.memory):
            if price["seller_id"] == seller_id and price["sku"] == sku:
                self.memory[i].update(price_update.model_dump())
                return self.memory[i]

        # Se não encontrar o registro, retorna None ou lança erro
        raise ValueError(f"Preço não encontrado para seller_id={seller_id}, sku={sku}")

    async def delete_by_seller_id_and_sku(self, seller_id: str, sku: str) -> None:
        """
        Remove um preco da memória com base no ID.

        :param seller_id: ID do vendedor.
        :param sku: Código do produto.
        :return: None
        """
        self.memory = [price for price in self.memory if not (price["seller_id"] == seller_id and price["sku"] == sku)]


__all__ = ["PriceRepository"]
