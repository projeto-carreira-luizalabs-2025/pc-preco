from uuid import UUID

from ..models import Price
from .base import AsyncMemoryRepository

from typing import Any, Dict, Optional, List


class PriceRepository(AsyncMemoryRepository[Price, UUID]):
    def __init__(self, memory: List[Dict[str, Any]] = None):
        """
        Inicializa o repositório com uma lista opcional de preços.

        :param memory: Lista opcional de dicionários representando objetos Price.
        """

        super().__init__(key_name="id", model_class=Price)
        self.memory = memory or []

    async def find_by_seller_id_and_sku(self, seller_id: str, sku: str) -> Optional[Dict[str, Any]]:
        """
        Busca um preço pela junção de seller_id + sku

        :param seller_id: ID do vendedor.
        :param sku: Código do produto.
        :return: Dicionário do price encontrado.
        """

        result = next((price for price in self.memory if price["seller_id"] == seller_id and price["sku"] == sku), None)

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
                self.memory[i].update(price_update)
                return self.memory[i]

    async def delete_by_seller_id_and_sku(self, seller_id: str, sku: str):
        """
        Remove um preco da memória com base no ID.

        :param seller_id: ID do vendedor.
        :param sku: Código do produto.
        :return: None
        """
        self.memory = [price for price in self.memory if not (price["seller_id"] == seller_id and price["sku"] == sku)]


__all__ = ["PriceRepository"]
