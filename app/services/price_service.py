from app.models.price_history_model import PriceHistory
from app.repositories.price_history_repository import PriceHistoryRepository
from app.services.price_history_service import PriceHistoryService
from ..common.exceptions.price_exceptions import PriceBadRequestException, PriceNotFoundException
from ..models import Price, PriceFilter
from ..repositories import PriceRepository
from .base import CrudService
from app.api.common.schemas import Paginator

from app.integrations.cache.redis_asyncio_adapter import RedisAsyncioAdapter
from app.integrations.queue.rabbitmq_adapter import RabbitMQProducer

import logging
import asyncio

logger = logging.getLogger(__name__)


class PriceService(CrudService[Price]):
    """
    Serviço responsável pelas regras de negócio relacionadas à entidade Preco.
    Fornece métodos para criação, atualização, busca e validação de preços.
    """

    repository: PriceRepository
    redis_adapter: RedisAsyncioAdapter
    queue_producer: RabbitMQProducer
    price_history_service: PriceHistoryService

    def __init__(
        self,
        repository: PriceRepository,
        price_history_repo: PriceHistoryRepository,
        price_history_service: PriceHistoryService,
        redis_adapter: RedisAsyncioAdapter,
        queue_producer: RabbitMQProducer,
    ):
        """
        Inicializa o serviço de preços com o repositório fornecido e o adaptador Redis.

        :param repository: Instância de PriceRepository para acesso aos dados.
        :param redis_adapter: Instância de RedisAsyncioAdapter para cache.
        """
        super().__init__(repository)
        self.redis_adapter = redis_adapter
        self.queue_producer = queue_producer
        self.price_history_repo = price_history_repo
        self.price_history_service = price_history_service

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
        Caso o preço esteja no cache, retorna a instância diretamente.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :return: Instância de Preco encontrada.
        :raises NotFoundException: Se não encontrar o preço.
        """
        cache_key = f"price:{seller_id}:{sku}"
        cached = await self.find_price_in_cache(seller_id, sku, cache_key)

        if cached is not None:
            return cached

        price_dict = await super().find_by_seller_id_and_sku(seller_id, sku)

        self._raise_not_found(seller_id, sku, price_dict is None)

        await self.redis_adapter.set_json(cache_key, price_dict.model_dump(mode="json"), expires_in_seconds=300)

        return Price.model_validate(price_dict)

    async def find_price_in_cache(self, seller_id: str, sku: str, cache_key: str) -> dict:
        """
        Busca um preço pelo seller_id e sku, utilizando cache.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :return: Instância de Preco encontrada.
        :raises NotFoundException: Se não encontrar o preço.
        """
        cached = await self.redis_adapter.get_json(cache_key)
        if cached is not None:
            logger.info(
                "Preço encontrado no cache para seller_id=%s, sku=%s",
                seller_id,
                sku,
                extra={"seller_id": seller_id, "sku": sku},
            )
            return Price.model_validate(cached)

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

        # Registra o histórico de preços após a criação
        price_history_data = price.model_dump()
        await self.price_history_service.create(PriceHistory(**price_history_data))

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

        # Verifica se o preço já possui alerta pendente
        self._verify_pending_alert(existing_price)

        merged_price_data = existing_price.model_dump()
        merged_price_data.update(update_data.model_dump(exclude_none=True))
        merged_price_data["updated_by"] = user_info.user

        try:
            merged_price = Price.model_validate(merged_price_data)
        except ValueError:
            logger.error(
                "Erro ao validar dados de atualização",
                extra={"update_data": update_data},
            )
            self._raise_bad_request(
                message="Dados inválidos para atualização.",
                field="update_data",
                value=update_data,
            )

        self._validate_positive_prices(merged_price)

        variation = self._detects_variation(
            old_por=existing_price.por,
            entity=merged_price,
        )
        if variation:
            merged_price.alerta_pendente = True

        updated = await super().update_by_seller_id_and_sku(seller_id, sku, merged_price)

        # Registra o histórico de preços após a atualização
        price_history_data = updated.model_dump(exclude={"id"})
        await self.price_history_service.create(PriceHistory(**price_history_data))

        # Remove o cache do preço atualizado
        cache_key = f"price:{seller_id}:{sku}"
        await self.redis_adapter.delete(cache_key)

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

        # Verifica se há alerta pendente antes de permitir atualização
        self._verify_pending_alert(price_found)

        # Verificação de valor de preço
        variation = self._detects_variation(
            old_por=price_found.por,
            entity=entity,
        )
        if variation:
            entity.alerta_pendente = True

        updated = await super().update_by_seller_id_and_sku(seller_id, sku, entity)

        # Registra o histórico de preços após a atualização
        price_history_data = updated.model_dump(exclude={"id"})
        await self.price_history_service.create(PriceHistory(**price_history_data))

        # Remove o cache do preço atualizado
        cache_key = f"price:{seller_id}:{sku}"
        await self.redis_adapter.delete(cache_key)

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

        # Remove o cache do preço deletado
        cache_key = f"price:{seller_id}:{sku}"
        await self.redis_adapter.delete(cache_key)

    def _verify_pending_alert(self, entity: Price) -> bool:
        """
        Verifica se o preço possui alerta pendente.

        :param entity: Instância de Preco a ser verificada.
        :return: True se o alerta estiver pendente, False caso contrário.
        """
        if entity.alerta_pendente:
            logger.info(
                "Alerta pendente para SKU %s do seller_id %s",
                entity.sku,
                entity.seller_id,
                extra={"seller_id": entity.seller_id, "sku": entity.sku},
            )
            self._raise_bad_request(
                "Não é possível atualizar o preço enquanto possuir alerta pendente.",
                field="alerta_pendente",
                value=True,
            )

    def _detects_variation(self, old_por, entity) -> bool:
        """
        Detecta se houve variação no preço 'por' (50%).

        :param old_por: Valor antigo do preço 'por'.
        :param new_por: Valor novo do preço 'por'.
        :return: True se houver variação, False caso contrário.
        """
        new_por = entity.por
        seller_id = entity.seller_id
        sku = entity.sku

        if old_por > 0 and abs(new_por - old_por) / old_por > 0.5:
            logger.warning(
                "Variação de preço superior a 50%% detectada para SKU %s: de %s para %s",
                sku,
                old_por,
                new_por,
                extra={"seller_id": seller_id, "sku": sku, "old_por": old_por, "new_por": new_por},
            )
            mensagem = f"Variação de preço superior a 50% detectada para {sku}: de {old_por} para {new_por}"
            alerta = {"seller_id": seller_id, "sku": sku, "mensagem": mensagem, "status": "pendente"}

            task = asyncio.create_task(self._call_producer(alerta))
            logger.info(
                "Tarefa criada para enviar evento para a fila: %s",
                task.get_name(),
                extra={"seller_id": seller_id, "sku": sku},
            )
            return True
        return False

    async def _call_producer(self, event):
        try:
            self.queue_producer.produce(event)
        except Exception:
            logger.exception("Falha enviar evento para a fila", extra={"evt": event})

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
            logger.warning("Valor inválido para %s: %s", field, value, extra={"field": field, "value": value})
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
            logger.warning(
                "Preço já cadastrado para seller_id: %s, sku: %s",
                seller_id,
                sku,
                extra={"seller_id": seller_id, "sku": sku},
            )
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
            logger.error(
                "Preço não encontrado para seller_id=%s, sku=%s",
                seller_id,
                sku,
                extra={"seller_id": seller_id, "sku": sku},
            )
            raise PriceNotFoundException(seller_id=seller_id, sku=sku)

    def _raise_bad_request(self, message: str, field: str = None, value=None):
        """
        Lança exceção de BadRequestException com detalhes do erro.

        :param message: Mensagem descritiva do erro.
        :param field: Campo relacionado ao erro.
        :param value: Valor que causou o erro (opcional).
        :raises BadRequestException: Sempre.
        """
        logger.error(
            "BadRequest: %s | field=%s | value=%s", message, field, value, extra={"field": field, "value": value}
        )
        raise PriceBadRequestException(message=message, field=field, value=value)
