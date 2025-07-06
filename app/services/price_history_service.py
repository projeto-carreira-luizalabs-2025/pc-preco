from app.models.price_filter_model import PriceFilter
from app.models.price_history_model import PriceHistory
from app.repositories.price_history_repository import PriceHistoryRepository
from .base import CrudService
from app.api.common.schemas import Paginator
from app.common.exceptions.price_exceptions import PriceNotFoundException
from pclogging import LoggingBuilder

LoggingBuilder.init(log_level="DEBUG")

logger = LoggingBuilder.get_logger(__name__)

class PriceHistoryService(CrudService[PriceHistory]):
    def __init__(self, repository: PriceHistoryRepository):
        super().__init__(repository)

    async def get_by_seller_id_and_sku(self, seller_id: str, sku: str, paginator: Paginator) -> list[PriceHistory]:
        """
        Busca o histórico de preços por seller_id e sku, com paginação.

        :param seller_id: Identificador do vendedor.
        :param sku: Código do produto.
        :param paginator: Objeto Paginator para controle de paginação.
        :return: Lista de instâncias de PriceHistory.
        :raises PriceNotFoundException: Se não houver histórico.
        """
        logger.info(
            f"Buscando histórico de preços para seller_id: {seller_id}, sku: {sku}"
        )

        filters = PriceFilter(seller_id=seller_id, sku=sku)
        results = await self.find(filters=filters, paginator=paginator)

        if not results:
            logger.warning(
                f"Histórico não encontrado para seller_id: {seller_id}, sku: {sku}"
            )
            raise PriceNotFoundException(seller_id=seller_id, sku=sku, message="Histórico de preço não encontrado.")

        logger.debug(f"Encontrados {len(results)} registros de histórico")
        return results