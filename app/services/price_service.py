from app.models.price_history_model import PriceHistory
from app.repositories.price_history_repository import PriceHistoryRepository
from ..common.exceptions.price_exceptions import PriceBadRequestException, PriceNotFoundException
from ..models import Price, PriceFilter
from ..repositories import PriceRepository
from .base import CrudService
from app.api.common.schemas import Paginator

from pclogging import LoggingBuilder

LoggingBuilder.init(log_level="DEBUG")

logger = LoggingBuilder.get_logger(__name__)


class PriceService(CrudService[Price]):
    """
    Serviço responsável pelas regras de negócio relacionadas à entidade Preco.
    Fornece métodos para criação, atualização, busca e validação de preços.
    """

    repository: PriceRepository

    def __init__(self, repository: PriceRepository, price_history_repo: PriceHistoryRepository):
        super().__init__(repository)
        self.price_history_repo = price_history_repo


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
        price_dict = await super().find_by_seller_id_and_sku(seller_id, sku)

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

        price = Price(**price_create.model_dump())
        created_price = await super().create(price)
        
        price_history_data = price.model_dump()
        await self.price_history_repo.create(PriceHistory(**price_history_data))
        
        return created_price

    async def patch(self, seller_id, sku, update_data, user_info) -> Price:
        """
        Atualiza campos de uma precificação.
        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :update_data: Dicionário contendo os campos a serem atualizados.
        :return: Instância de Preco atualizada.
        :raises NotFoundException: Se não encontrar o preço.
        :raises BadRequestException: Se valores inválidos forem informados.
        """

        price_dict = await super().find_by_seller_id_and_sku(seller_id, sku)
        self._raise_not_found(seller_id, sku, price_dict is None)

        existing_price = Price.model_validate(price_dict)

        merged_price_data = existing_price.model_dump()
        merged_price_data.update(update_data.model_dump(exclude_none=True))

        merged_price_data["updated_by"] = user_info.user

        try:
            merged_price = Price.model_validate(merged_price_data)
        except ValueError:
            logger.error(f"Erro ao validar dados de atualização: {update_data}")
            self._raise_bad_request(
                message="Dados inválidos para atualização.",
                field="update_data",
                value=update_data,
            )

        self._validate_positive_prices(merged_price)
        updated = await super().update_by_seller_id_and_sku(seller_id, sku, merged_price)
        
        await self.price_history_repo.create(PriceHistory(**updated.model_dump()))
        
        return updated

    async def update(self, seller_id, sku, entity: Price) -> Price:
        """
        Atualiza uma precificação existente com novos valores.
        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :param entity: Objeto contendo os novos dados do preço.
        :return: Instância de Preco atualizada.
        :raises NotFoundException: Se não encontrar o preço.
        :raises BadRequestException: Se valores inválidos forem informados.
        """
        price_found = await super().find_by_seller_id_and_sku(seller_id, sku)
        self._raise_not_found(seller_id, sku, price_found is None)
        self._validate_positive_prices(entity)
        updated = await super().update_by_seller_id_and_sku(seller_id, sku, entity)
        
        price_history_data = updated.model_dump()
        await self.price_history_repo.create(PriceHistory(**price_history_data))
        
        return updated

    async def delete(self, seller_id: str, sku: str):
        """
        Remove um preço baseado em seller_id e sku.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :raises NotFoundException: Se o preço não for encontrado.
        """
        price_found = await super().find_by_seller_id_and_sku(seller_id, sku)
        self._raise_not_found(seller_id, sku, price_found is None)

        deleted = await super().delete_by_seller_id_and_sku(seller_id, sku)
        if deleted is False:
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
        logger.debug(f"Validando se {field} é positivo: {value}")
        if value <= 0:
            logger.warning(f"Valor inválido para {field}: {value}")
            self._raise_bad_request(f"{field} deve ser maior que zero.", field, value)

    async def _validate_non_existent_price(self, seller_id: str, sku: str):
        """
        Verifica se já existe um preço cadastrado para o seller_id e sku informados.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :raises BadRequestException: Se já existir preço cadastrado.
        """
        price_found = await super().find_by_seller_id_and_sku(seller_id, sku)
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
            logger.error(f"Preço não encontrado para seller_id: {seller_id}, sku: {sku}")
            raise PriceNotFoundException(seller_id=seller_id, sku=sku)

    def _raise_bad_request(self, message: str, field: str = None, value=None):
        """
        Lança exceção de BadRequestException com detalhes do erro.

        :param message: Mensagem descritiva do erro.
        :param field: Campo relacionado ao erro.
        :param value: Valor que causou o erro (opcional).
        :raises BadRequestException: Sempre.
        """
        logger.error(f"BadRequest: {message} | field={field} | value={value}")
        raise PriceBadRequestException(message=message, field=field, value=value)
