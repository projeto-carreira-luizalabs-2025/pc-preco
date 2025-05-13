from uuid import UUID

from app.common.exceptions import NotFoundException

from ..models import Preco
from .base import AsyncMemoryRepository


class PrecoRepository(AsyncMemoryRepository[Preco, UUID]):

    async def find_by_name(self, name: str) -> Preco:
        """
        Busca um alguma coisa pelo nome.
        """
        result = next((s for s in self.memory if s["name"] == name), None)
        if result:
            return result
        raise NotFoundException()

    async def find_by_seller_id_and_sku(self, seller_id: str, sku: str) -> Preco:
        """
        Busca um preço pela junção de seller_id + sku
        """

        result = next((preco for preco in self.memory if preco.seller_id == seller_id and preco.sku == sku), None)

        return result

    async def delete_by_seller_id_and_sku(self, seller_id: str, sku:str):
        """
        Remove um preco da memória com base no ID.
        """
        self.memory = [
            preco for preco in self.memory 
            if not (preco.seller_id == seller_id and preco.sku == sku)
        ]

__all__ = ["PrecoRepository"]
