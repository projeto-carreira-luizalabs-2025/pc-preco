from typing import Any, Dict

from ..common.exceptions.price_exceptions import PriceBadRequestException, PriceNotFoundException
from ..models import Price, PriceFilter
from ..repositories import PriceRepository
from .base import CrudService
from app.api.common.schemas import Paginator


class PriceService(CrudService[Price, str]):
    """
    Serviço responsável pelas regras de negócio relacionadas à entidade Preco.
    Fornece métodos para criação, atualização, busca e validação de preços.
    """

    repository: PriceRepository

    def __init__(self, repository: PriceRepository):
        """
        Inicializa o serviço de preços com o repositório fornecido.

        :param repository: Instância de PriceRepository para acesso aos dados.
        """
        super().__init__(repository)

    async def get_filtered(self, paginator=Paginator, filters=dict) -> list[Price]:
        """
        Recupera uma lista de preços filtrados e paginados.

        :param paginator: Objeto Paginator para controle de paginação.
        :param filters: Dicionário de filtros a serem aplicados na busca.
        :return: Lista de instâncias de Preco filtradas e paginadas.
        """

        # Cria o dicionário de filtros apenas com os valores que não são None
        current_filters = {key: value for key, value in filters.items() if value is not None}

        filter_model = PriceFilter(**current_filters)

        return await self.find(filters=filter_model, paginator=paginator)

    async def get_by_seller_id_and_sku(self, seller_id: str, sku: str) -> Price:
        """
        Busca um preço pelo seller_id e sku.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :return: Instância de Preco encontrada.
        :raises NotFoundException: Se não encontrar o preço.
        """
        price_dict = await self.repository.find_by_seller_id_and_sku(seller_id, sku)

        self._raise_not_found(seller_id, sku, price_dict is None)

        # Garantimos que price_dict não é None neste ponto, podemos usá-lo com segurança
        return Price.model_validate(price_dict)

    async def create(self, price_create: Price) -> Price:
        """
        Cria uma nova precificação após validações de unicidade e valores positivos.

        :param price_create: Objeto contendo os dados para criação do preço.
        :return: Instância de Preco criada.
        :raises BadRequestException: Se já existir preço para o produto ou valores inválidos.
        """
        await self._validate_non_existent_price(price_create.seller_id, price_create.sku)
        self._validate_positive_prices(price_create)
        # Converte PrecoCreate para Preco, gerando o id automaticamente
        price = Price(**price_create.model_dump())
        return await super().create(price)

    async def patch(self, entity_id: str, update_data: Dict[str, Any]) -> Price:
        """
        Atualiza campos de uma precificação.
        :param entity_id: Chave composta seller_id|sku (formato: seller_id|sku)
        :update_data: Dicionário contendo os campos a serem atualizados.
        :return: Instância de Preco atualizada.
        :raises NotFoundException: Se não encontrar o preço.
        :raises BadRequestException: Se valores inválidos forem informados.
        """
        # Espera-se que entity_id seja 'seller_id|sku'
        try:
            seller_id, sku = entity_id.split("|", 1)
        except ValueError:
            raise PriceBadRequestException(
                message="entity_id deve ser no formato 'seller_id|sku'",
                field="entity_id",
                value=entity_id,
            )
        price_dict = await self.repository.find_by_seller_id_and_sku(seller_id, sku)
        self._raise_not_found(seller_id, sku, price_dict is None)

        existing_price = Price.model_validate(price_dict)

        merged_price_data = existing_price.model_dump()
        merged_price_data.update(update_data)

        try:
            merged_price = Price.model_validate(merged_price_data)
        except ValueError:
            raise PriceBadRequestException(
                message="Dados inválidos para atualização.",
                field="update_data",
                value=update_data,
            )

        self._validate_positive_prices(merged_price)
        updated = await self.repository.update_by_seller_id_and_sku(seller_id, sku, merged_price)
        return updated

    async def update(self, entity_id: str, entity: Price) -> Price:
        """
        Atualiza uma precificação existente com novos valores.
        :param entity_id: Chave composta seller_id|sku (formato: seller_id|sku)
        :param entity: Objeto contendo os novos dados do preço.
        :return: Instância de Preco atualizada.
        :raises NotFoundException: Se não encontrar o preço.
        :raises BadRequestException: Se valores inválidos forem informados.
        """
        # Espera-se que entity_id seja 'seller_id|sku'
        try:
            seller_id, sku = entity_id.split("|", 1)
        except ValueError:
            raise PriceBadRequestException(
                message="entity_id deve ser no formato 'seller_id|sku'",
                field="entity_id",
                value=entity_id,
            )
        price_found = await self.repository.find_by_seller_id_and_sku(seller_id, sku)
        self._raise_not_found(seller_id, sku, price_found is None)
        self._validate_positive_prices(entity)
        updated = await self.repository.update_by_seller_id_and_sku(seller_id, sku, entity)
        return updated

    async def delete(self, seller_id: str, sku: str):
        """
        Remove um preço baseado em seller_id e sku.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :raises NotFoundException: Se o preço não for encontrado.
        """
        price_found = await self.repository.find_by_seller_id_and_sku(seller_id, sku)
        self._raise_not_found(seller_id, sku, price_found is None)
        deleted = await self.repository.delete_by_seller_id_and_sku(seller_id, sku)
        if not deleted:
            self._raise_bad_request(
                message="Erro ao deletar preço.",
                value=sku,
            )

    def _validate_positive_prices(self, price):
        """
        Valida se os atributos 'de' e 'por' são positivos.

        :param price: Objeto de preço a ser validado.
        """
        self._validate_positives(price.de, "de")
        self._validate_positives(price.por, "por")

    def _validate_positives(self, value, field: str):
        """
        Valida se o valor fornecido é maior que zero.

        :param field: Nome do campo que está sendo validado.
        :param value: Valor númerico a ser validado (opcional).
        :raises BadRequestException: Se algum valor for menor ou igual a zero.
        """
        if value <= 0:
            self._raise_bad_request(f"{field} deve ser maior que zero.", field, value)

    async def _validate_non_existent_price(self, seller_id: str, sku: str):
        """
        Verifica se já existe um preço cadastrado para o seller_id e sku informados.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :raises BadRequestException: Se já existir preço cadastrado.
        """
        price_found = await self.repository.find_by_seller_id_and_sku(seller_id, sku)
        if price_found is not None:
            self._raise_bad_request("Preço para produto já cadastrado.", "sku")

    @staticmethod
    def _raise_not_found(seller_id: str, sku: str, condition: bool = True):
        """
        Lança exceção de NotFoundException com detalhes do erro.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :raises NotFoundException: Sempre.
        """
        if condition:
            raise PriceNotFoundException(seller_id=seller_id, sku=sku)

    def _raise_bad_request(self, message: str, field: str = None, value=None):
        """
        Lança exceção de BadRequestException com detalhes do erro.

        :param message: Mensagem descritiva do erro.
        :param field: Campo relacionado ao erro.
        :param value: Valor que causou o erro (opcional).
        :raises BadRequestException: Sempre.
        """
        raise PriceBadRequestException(message=message, field=field, value=value)
