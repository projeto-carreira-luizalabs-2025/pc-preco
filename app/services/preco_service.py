from uuid import UUID

from ..models import Preco
from ..repositories import PrecoRepository
from .base import CrudService

from ..common.exceptions import BadRequestException, NotFoundException
from ..api.common.schemas.response import ErrorDetail


class PrecoService(CrudService[Preco, UUID]):
    """
    Serviço responsável pelas regras de negócio relacionadas à entidade Preco.
    Fornece métodos para criação, atualização, busca e validação de preços.
    """

    repository: PrecoRepository

    def __init__(self, repository: PrecoRepository):
        """
        Inicializa o serviço de preços com o repositório fornecido.

        :param repository: Instância de PrecoRepository para acesso aos dados.
        """
        super().__init__(repository)

    async def find_by_seller_id_and_sku(self, seller_id: str, sku: str) -> Preco:
        """
        Busca um preço pelo seller_id e sku.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :return: Instância de Preco encontrada.
        :raises NotFoundException: Se não encontrar o preço.
        """
        preco_encontrado = await self.repository.find_by_seller_id_and_sku(seller_id, sku)
        if preco_encontrado is None:
            self._raise_not_found(seller_id, sku)
        return preco_encontrado

    async def create_preco(self, preco) -> Preco:
        """
        Cria uma nova precificação após validações de unicidade e valores positivos.

        :param preco: Objeto contendo os dados para criação do preço.
        :return: Instância de Preco criada.
        :raises BadRequestException: Se já existir preço para o produto ou valores inválidos.
        """
        await self._validate_preco_nao_existe(preco.seller_id, preco.sku)
        self._validate_precos_positivos(preco)
        return await self.create(preco)

    async def update_preco(self, seller_id: str, sku: str, preco) -> Preco:
        """
        Atualiza uma precificação existente com novos valores.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :param preco: Objeto contendo os novos dados do preço.
        :return: Instância de Preco atualizada.
        :raises NotFoundException: Se não encontrar o preço.
        :raises BadRequestException: Se valores inválidos forem informados.
        """
        preco_encontrado = await self.repository.find_by_seller_id_and_sku(seller_id, sku)
        if preco_encontrado is None:
            self._raise_not_found(seller_id, sku)
        self._validate_precos_positivos(preco)
        return await self.update(preco_encontrado.id, preco)

    def _validate_precos_positivos(self, preco):
        """
        Valida se os valores de preco_de e preco_por são positivos.

        :param preco: Objeto de preço a ser validado.
        :raises BadRequestException: Se algum valor for menor ou igual a zero.
        """
        if preco.preco_de <= 0:
            self._raise_bad_request("preco_de deve ser maior que zero.", "preco_de")
        if preco.preco_por <= 0:
            self._raise_bad_request("preco_por deve ser maior que zero.", "preco_por")

    async def _validate_preco_nao_existe(self, seller_id: str, sku: str):
        """
        Verifica se já existe um preço cadastrado para o seller_id e sku informados.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :raises BadRequestException: Se já existir preço cadastrado.
        """
        preco_encontrado = await self.repository.find_by_seller_id_and_sku(seller_id, sku)
        if preco_encontrado:
            self._raise_bad_request("Preço para produto já cadastrado.", "sku")

    def _raise_not_found(self, seller_id: str, sku: str):
        """
        Lança exceção de NotFoundException com detalhes do erro.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :raises NotFoundException: Sempre.
        """
        raise NotFoundException(details=[
            ErrorDetail(
                message="Preço para produto não encontrado.",
                location="path",
                slug="preco_nao_encontrado",
                field="sku",
                ctx={"seller_id": seller_id, "sku": sku}
            )
        ])

    def _raise_bad_request(self, message: str, field: str):
        """
        Lança exceção de BadRequestException com detalhes do erro.

        :param message: Mensagem descritiva do erro.
        :param field: Campo relacionado ao erro.
        :raises BadRequestException: Sempre.
        """
        raise BadRequestException(details=[
            ErrorDetail(
                message=message,
                location="body",
                slug="preco_invalido",
                field=field
            )
        ])
