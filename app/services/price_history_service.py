
from app.models.price_history_model import PriceHistory
from app.repositories.price_history_repository import PriceHistoryRepository
from .base import CrudService

class PriceHistoryService(CrudService[PriceHistory]):
    def __init__(self, repository: PriceHistoryRepository):
        super().__init__(repository)
