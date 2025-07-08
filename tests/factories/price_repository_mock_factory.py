from typing import Dict, Tuple
from unittest.mock import AsyncMock, Mock, MagicMock
from datetime import datetime, timezone

from app.models import Price
from app.repositories import PriceRepository
from app.integrations.database.sqlalchemy_client import SQLAlchemyClient


class AsyncSessionMock(MagicMock):
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class PriceRepositoryMockFactory:
    """
    Factory para criar mocks do PriceRepository com comportamentos padronizados.
    """

    @staticmethod
    def create_mock_repository(initial_data: Dict[Tuple[str, str], Price] = None) -> PriceRepository:
        """
        Cria um mock do PriceRepository com comportamentos simulados.

        Args:
            initial_data: Dicionário com dados iniciais no formato {(seller_id, sku): Price}
                Se None, usa dados padrão.

        Returns:
            PriceRepository mockado com comportamentos simulados
        """
        mock_sql_client = Mock(spec=SQLAlchemyClient)

        # Mock dos métodos assíncronos do SQL client
        mock_sql_client.create = AsyncMock()
        mock_sql_client.find_by_seller_id_and_sku = AsyncMock()
        mock_sql_client.update_by_seller_id_and_sku = AsyncMock()
        mock_sql_client.delete_by_seller_id_and_sku = AsyncMock()
        # Mock do context manager assíncrono
        mock_sql_client.make_session = AsyncMock(return_value=AsyncSessionMock())

        repository = PriceRepository(sql_client=mock_sql_client)

        # Dados iniciais padrão se não fornecidos
        if initial_data is None:
            initial_data = {
                ("1", "A"): Price(seller_id="1", sku="A", de=100, por=90),
                ("2", "B"): Price(seller_id="2", sku="B", de=200, por=180),
            }

        # Banco simulado
        simulated_db = initial_data.copy()

        # Implementações dos comportamentos mockados
        async def mock_create(price: Price):
            price.created_at = datetime.now(timezone.utc)
            simulated_db[(price.seller_id, price.sku)] = price
            return price

        async def mock_find_by_seller_id_and_sku(seller_id: str, sku: str):
            return simulated_db.get((seller_id, sku))

        async def mock_update_by_seller_id_and_sku(seller_id: str, sku: str, price_update: Price):
            if (seller_id, sku) in simulated_db:
                updated_price = price_update
                updated_price.seller_id = seller_id
                updated_price.sku = sku
                simulated_db[(seller_id, sku)] = updated_price
                return updated_price
            raise ValueError("Price not found")

        async def mock_delete_by_seller_id_and_sku(seller_id: str, sku: str):
            if (seller_id, sku) in simulated_db:
                del simulated_db[(seller_id, sku)]
                return True
            return False

        async def mock_find(*args, **kwargs):
            # Retorna todos os preços simulados como lista
            return list(simulated_db.values())

        # Aplicar os mocks
        repository.create = AsyncMock(side_effect=mock_create)
        repository.find_by_seller_id_and_sku = AsyncMock(side_effect=mock_find_by_seller_id_and_sku)
        repository.update_by_seller_id_and_sku = AsyncMock(side_effect=mock_update_by_seller_id_and_sku)
        repository.delete_by_seller_id_and_sku = AsyncMock(side_effect=mock_delete_by_seller_id_and_sku)
        repository.find = AsyncMock(side_effect=mock_find)

        # Expor o banco simulado para inspeção/manipulação nos testes se necessário
        repository._simulated_db = simulated_db

        return repository

    @staticmethod
    def create_empty_mock_repository() -> PriceRepository:
        """
        Cria um mock do PriceRepository sem dados iniciais.

        Returns:
            PriceRepository mockado vazio
        """
        return PriceRepositoryMockFactory.create_mock_repository(initial_data={})

    @staticmethod
    def create_mock_repository_with_custom_data(prices: list[Price]) -> PriceRepository:
        """
        Cria um mock do PriceRepository com dados customizados.

        Args:
            prices: Lista de objetos Price para popular o repositório

        Returns:
            PriceRepository mockado com os dados fornecidos
        """
        initial_data = {(price.seller_id, price.sku): price for price in prices}
        return PriceRepositoryMockFactory.create_mock_repository(initial_data=initial_data)
