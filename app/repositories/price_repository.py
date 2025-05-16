from uuid import UUID

from app.common.exceptions import NotFoundException

from ..models import Price
from .base import AsyncMemoryRepository


class PriceRepository(AsyncMemoryRepository[Price, UUID]):
    def __init__(self, memory: list[Price]):
        super().__init__(key_name="id", model_class=Price)
        self.memory = memory or []

    async def find_by_seller_id_and_sku(self, seller_id: str, sku: str) -> Price:
        """
        Busca um preço pela junção de seller_id + sku
        """

        result = next((price for price in self.memory if price["seller_id"] == seller_id and price["sku"] == sku), None)

        return result
    
    async def update_by_seller_id_and_sku(self, seller_id: str, sku: str, price_update: dict) -> Price:
        """
        Atualiza um preço na memória pela junção de seller_id + sku.
        """
        for i, price in enumerate(self.memory):
            if price["seller_id"] == seller_id and price["sku"] == sku:
                self.memory[i].update(price_update)
                return self.memory[i]


    async def delete_by_seller_id_and_sku(self, seller_id: str, sku: str):
        """
        Remove um preco da memória com base no ID.
        """
        self.memory = [price for price in self.memory if not (price["seller_id"] == seller_id and price["sku"] == sku)]


__all__ = ["PriceRepository"]
