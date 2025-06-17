from typing import Dict, Tuple
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timezone

from app.models import Price
from app.repositories import PriceRepository
from app.integrations.database.sqlalchemy_client import SQLAlchemyClient

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
        
        repository = PriceRepository(sql_client=mock_sql_client)
        
        # Dados iniciais padrão se não fornecidos
        if initial_data is None:
            initial_data = {
                ("1", "A"): Price(seller_id="1", sku="A", de=100, por = 90),
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
            price = simulated_db.get((seller_id, sku))
            if price:
                # Retorna como dicionário, como esperado pelos testes
                return {
                    "seller_id": price.seller_id,
                    "sku": price.sku,
                    "de": price.de,
                    "por": price.por,
                    "created_at": getattr(price, 'created_at', None),
                    "updated_at": getattr(price, 'updated_at', None),
                    "created_by": getattr(price, 'created_by', None),
                    "updated_by": getattr(price, 'updated_by', None),
                    "audit_created_at": getattr(price, 'audit_created_at', None),
                    "audit_updated_at": getattr(price, 'audit_updated_at', None),
                }
            return None
        
        async def mock_update_by_seller_id_and_sku(seller_id: str, sku: str, price_update: Price):
            if (seller_id, sku) in simulated_db:
                updated_price = price_update
                updated_price.seller_id = seller_id
                updated_price.sku = sku
                simulated_db[(seller_id, sku)] = updated_price
                return price_update.model_dump()
            raise ValueError("Price not found")
            
        async def mock_delete_by_seller_id_and_sku(seller_id: str, sku: str):
            if (seller_id, sku) in simulated_db:
                del simulated_db[(seller_id, sku)]
                return True
            return False
        
        # Aplicar os mocks
        repository.create = AsyncMock(side_effect=mock_create)
        repository.find_by_seller_id_and_sku = AsyncMock(side_effect=mock_find_by_seller_id_and_sku)
        repository.update_by_seller_id_and_sku = AsyncMock(side_effect=mock_update_by_seller_id_and_sku)
        repository.delete_by_seller_id_and_sku = AsyncMock(side_effect=mock_delete_by_seller_id_and_sku)
        
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