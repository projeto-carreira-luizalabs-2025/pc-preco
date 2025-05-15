from uuid import UUID

from app.common.exceptions import NotFoundException

from ..models import Preco
from .base import AsyncMemoryRepository


class PrecoRepository(AsyncMemoryRepository[Preco, UUID]):
    def __init__(self, memory: list[Preco]):
        super().__init__(key_name="id", model_class=Preco)
        self.memory = memory or []

    async def find_by_seller_id_and_sku(self, seller_id: str, sku: str) -> Preco:
        """
        Busca um preço pela junção de seller_id + sku
        """

        result = next((preco for preco in self.memory if preco["seller_id"] == seller_id and preco["sku"] == sku), None)

        return result

    async def delete_by_seller_id_and_sku(self, seller_id: str, sku: str):
        """
        Remove um preco da memória com base no ID.
        """
        self.memory = [preco for preco in self.memory if not (preco["seller_id"] == seller_id and preco["sku"] == sku)]


__all__ = ["PrecoRepository"]
