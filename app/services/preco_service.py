from ..models import Preco
from ..repositories import PrecoRepository
from .base import CrudService


class PrecoService(CrudService[Preco, int]):  # PrecoService herda os métodos genéricos de CRUD do "CrudService"
    def __init__(self, repository: PrecoRepository):
        super().__init__(repository)

    async def find_by_name(self, name: str) -> Preco:
        """
        Busca um Preco pelo nome.
        """
        return await self.repository.find_by_name(name=name)

    async def find_by_seller_id_and_sku(self, seller_id: str, sku: str) -> Preco:
        """
        Busca um preço pela junção de seller_id + sku
        """
        return await self.repository.find_by_seller_id_and_sku(seller_id, sku)
