from typing import Optional
from uuid import UUID

from ..models import Preco
from .base import AsyncMemoryRepository


class PrecoRepository(AsyncMemoryRepository[Preco, UUID]):
    """
    Repositório para operações de persistência da entidade Preco.
    """

    async def find_by_seller_id_and_sku(self, seller_id: str, sku: str) -> Optional[Preco]:
        """
        Busca um preço pela junção de seller_id + sku

        :param seller_id: Identificador do vendedor
        :param sku: Código do produto
        :return: Instância de Preco encontrada ou None
        """
        result = next((preco for preco in self.memory if preco.seller_id == seller_id and preco.sku == sku), None)
        return result

    async def delete_by_seller_id_and_sku(self, seller_id: str, sku: str) -> None:
        """
        Remove um preço da memória com base no seller_id e sku.

        :param seller_id: Identificador do vendedor
        :param sku: Código do produto
        """
        self.memory = [preco for preco in self.memory if not (preco.seller_id == seller_id and preco.sku == sku)]


__all__ = ["PrecoRepository"]
