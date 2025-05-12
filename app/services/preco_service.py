from ..models import Preco
from ..repositories import PrecoRepository
from .base import CrudService

from ..common.exceptions import BadRequestException, NotFoundException
from ..api.common.schemas.response import ErrorDetail


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
        Busca uma precificação pela junção de seller_id + sku
        """

        # Verificar se a precificação existe
        preco_encontrado = await self.repository.find_by_seller_id_and_sku(seller_id, sku)

        if preco_encontrado == None:
            raise NotFoundException(details=[ErrorDetail(message="Preço para produto não encontrado.")])

        return preco_encontrado

    async def create_preco(self, preco) -> Preco:
        """
        Cria uma precificação
        """

        # Verificar se a precificação já existe
        preco_encontrado = await self.repository.find_by_seller_id_and_sku(preco.seller_id, preco.sku)

        if preco_encontrado:
            raise BadRequestException(details=[ErrorDetail(message="Preço para produto já cadastrado.")])

        if preco.preco_de <= 0:
            raise BadRequestException(details=[ErrorDetail(message="preco_de deve ser maior que zero.")])
        if preco.preco_por <= 0:
            raise BadRequestException(details=[ErrorDetail(message="preco_por deve ser maior que zero.")])

        return await self.create(preco)
