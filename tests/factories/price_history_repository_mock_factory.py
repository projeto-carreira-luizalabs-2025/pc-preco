from datetime import datetime, timezone
from typing import Dict, Tuple
from unittest.mock import AsyncMock, MagicMock, Mock

from app.integrations.database.sqlalchemy_client import SQLAlchemyClient
from app.models.price_history_model import PriceHistory
from app.repositories.price_history_repository import PriceHistoryRepository


class AsyncSessionMock(MagicMock):
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class PriceHistoryRepositoryMockFactory:
    @staticmethod
    def create_mock_repository(
        initial_data: Dict[Tuple[str, str], list[PriceHistory]] = None,
    ) -> PriceHistoryRepository:
        mock_sql_client = Mock(spec=SQLAlchemyClient)
        mock_sql_client.create = AsyncMock()
        mock_sql_client.find_by_seller_id_and_sku = AsyncMock()
        mock_sql_client.find = AsyncMock()
        mock_sql_client.make_session = AsyncMock(return_value=AsyncSessionMock())

        repository = PriceHistoryRepository(sql_client=mock_sql_client)

        if initial_data is None:
            initial_data = {
                ("1", "A"): [
                    PriceHistory(seller_id="1", sku="A", de=100, por=90, registered_at=datetime.now(timezone.utc))
                ],
                ("2", "B"): [
                    PriceHistory(seller_id="2", sku="B", de=200, por=180, registered_at=datetime.now(timezone.utc))
                ],
            }

        simulated_db = initial_data.copy()

        async def mock_create(price_history: PriceHistory):
            key = (price_history.seller_id, price_history.sku)
            if key not in simulated_db:
                simulated_db[key] = []
            simulated_db[key].append(price_history)
            return price_history

        async def mock_find_by_seller_id_and_sku(seller_id: str, sku: str):
            return simulated_db.get((seller_id, sku), [])

        async def mock_find(*args, **kwargs):
            # Retorna todos os históricos simulados como lista
            all_histories = []
            for histories in simulated_db.values():
                all_histories.extend(histories)
            return all_histories

        repository.create = AsyncMock(side_effect=mock_create)
        repository.find_by_seller_id_and_sku = AsyncMock(side_effect=mock_find_by_seller_id_and_sku)
        repository.find = AsyncMock(side_effect=mock_find)
        repository._simulated_db = simulated_db

        return repository

    @staticmethod
    def create_empty_mock_repository() -> PriceHistoryRepository:
        return PriceHistoryRepositoryMockFactory.create_mock_repository(initial_data={})

    @staticmethod
    def create_mock_repository_with_custom_data(histories: list[PriceHistory]) -> PriceHistoryRepository:
        initial_data = {}
        for history in histories:
            key = (history.seller_id, history.sku)
            if key not in initial_data:
                initial_data[key] = []
            initial_data[key].append(history)
        return PriceHistoryRepositoryMockFactory.create_mock_repository(initial_data=initial_data)
