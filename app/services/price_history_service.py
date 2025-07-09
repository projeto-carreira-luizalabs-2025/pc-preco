from pclogging import LoggingBuilder

from app.api.common.schemas import Paginator
from app.common.exceptions.price_exceptions import PriceNotFoundException
from app.models.price_filter_model import PriceFilter
from app.models.price_history_model import PriceHistory
from app.repositories.price_history_repository import PriceHistoryRepository

from .base import CrudService

LoggingBuilder.init(log_level="DEBUG")

logger = LoggingBuilder.get_logger(__name__)


class PriceHistoryService(CrudService[PriceHistory]):

    def __init__(self, repository: PriceHistoryRepository):
        super().__init__(repository)

    async def get_by_seller_id_and_sku(self, seller_id: str, sku: str, paginator: Paginator) -> list[PriceHistory]:
        """
        Busca o histórico de preços de um produto por seller_id e sku.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :param paginator: Objeto Paginator para controle de paginação.
        :return: Lista de instâncias de PriceHistory.
        :raises PriceNotFoundException: Se não houver histórico.
        """

        logger.info(f"Buscando histórico de preços para seller_id: {seller_id}, sku: {sku}")

        filters = PriceFilter(seller_id=seller_id, sku=sku)
        results = await self.find(filters=filters, paginator=paginator)

        if not results:
            logger.warning(f"Histórico não encontrado para seller_id: {seller_id}, sku: {sku}")
            raise PriceNotFoundException(seller_id=seller_id, sku=sku)

        logger.debug(f"Encontrados {len(results)} registros de histórico")

        return results

    async def get_last_n_prices(self, seller_id: str, sku: str, n: int = 5) -> list[PriceHistory]:
        """
        Recupera os últimos n preços de um produto por seller_id e sku.
        """

        logger.info(f"Recuperando os últimos {n} preços para seller_id: {seller_id}, sku: {sku}")

        filters = PriceFilter(seller_id=seller_id, sku=sku)
        # Cria um paginator manualmente, ordenando por registered_at desc
        paginator = Paginator(request_path="/", limit=n, offset=0, sort="registered_at:desc")
        results = await self.find(filters=filters, paginator=paginator)

        if not results:
            logger.warning(f"Nenhum histórico encontrado para seller_id: {seller_id}, sku: {sku}")
            raise PriceNotFoundException(seller_id=seller_id, sku=sku)

        logger.debug(f"Encontrados {len(results)} registros de histórico")
        return results
