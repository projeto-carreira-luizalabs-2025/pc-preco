from typing import Dict, Tuple
from unittest.mock import AsyncMock, Mock, MagicMock
from datetime import datetime, timezone

from app.models import Alert
from app.repositories.alert_repository import AlertRepository
from app.integrations.database.sqlalchemy_client import SQLAlchemyClient


class AsyncSessionMock(MagicMock):
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class AlertRepositoryMockFactory:
    @staticmethod
    def create_mock_repository(initial_data: Dict[Tuple[str, str], Alert] = None) -> AlertRepository:
        mock_sql_client = Mock(spec=SQLAlchemyClient)
        mock_sql_client.create = AsyncMock()
        mock_sql_client.find_by_seller_id_and_sku = AsyncMock()
        mock_sql_client.update_by_seller_id_and_sku = AsyncMock()
        mock_sql_client.delete_by_seller_id_and_sku = AsyncMock()
        mock_sql_client.find = AsyncMock()
        mock_sql_client.make_session = AsyncMock(return_value=AsyncSessionMock())

        repository = AlertRepository(sql_client=mock_sql_client)

        if initial_data is None:
            initial_data = {
                ("1", "A"): Alert(seller_id="1", sku="A", mensagem="Alerta 1", status="pendente"),
                ("2", "B"): Alert(seller_id="2", sku="B", mensagem="Alerta 2", status="pendente"),
            }

        simulated_db = initial_data.copy()

        async def mock_create(alert: Alert):
            simulated_db[(alert.seller_id, alert.sku)] = alert
            return alert

        async def mock_find_by_seller_id_and_sku(seller_id: str, sku: str):
            return simulated_db.get((seller_id, sku))

        async def mock_update_by_seller_id_and_sku(seller_id: str, sku: str, alert_update: Alert):
            if (seller_id, sku) in simulated_db:
                updated_alert = alert_update
                updated_alert.seller_id = seller_id
                updated_alert.sku = sku
                simulated_db[(seller_id, sku)] = updated_alert
                return updated_alert
            raise ValueError("Alert not found")

        async def mock_delete_by_seller_id_and_sku(seller_id: str, sku: str):
            if (seller_id, sku) in simulated_db:
                del simulated_db[(seller_id, sku)]
                return True
            return False

        async def mock_find(*args, **kwargs):
            return list(simulated_db.values())

        repository.create = AsyncMock(side_effect=mock_create)
        repository.find_by_seller_id_and_sku = AsyncMock(side_effect=mock_find_by_seller_id_and_sku)
        repository.update_by_seller_id_and_sku = AsyncMock(side_effect=mock_update_by_seller_id_and_sku)
        repository.delete_by_seller_id_and_sku = AsyncMock(side_effect=mock_delete_by_seller_id_and_sku)
        repository.find = AsyncMock(side_effect=mock_find)
        repository._simulated_db = simulated_db

        return repository

    @staticmethod
    def create_empty_mock_repository() -> AlertRepository:
        return AlertRepositoryMockFactory.create_mock_repository(initial_data={})

    @staticmethod
    def create_mock_repository_with_custom_data(alerts: list[Alert]) -> AlertRepository:
        initial_data = {(alert.seller_id, alert.sku): alert for alert in alerts}
        return AlertRepositoryMockFactory.create_mock_repository(initial_data=initial_data)
