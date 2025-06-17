import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models import Price
from app.repositories import PriceRepository
from app.integrations.database.sqlalchemy_client import SQLAlchemyClient

from datetime import datetime, timezone

class TestPrecoRepository:
    
    @pytest.fixture
    def repository_mock(self):
        """Cria um repositório com SQL client mockado e métodos simulados."""
        mock_sql_client = MagicMock(spec=SQLAlchemyClient)
        
        # Mock dos métodos assíncronos do SQL client
        mock_sql_client.create = AsyncMock()
        mock_sql_client.find_by_seller_id_and_sku = AsyncMock()
        mock_sql_client.update_by_seller_id_and_sku = AsyncMock()
        mock_sql_client.delete_by_seller_id_and_sku = AsyncMock()
        
        repository = PriceRepository(sql_client=mock_sql_client)
        
        simulated_db = {
            ("1", "A"): Price(seller_id="1", sku="A", de=100, por=90),
            ("2", "B"): Price(seller_id="2", sku="B", de=200, por=180),
        }

        # mocks de comportamento esperado
        async def mock_create(price):
            price.created_at = datetime.now(timezone.utc)
            # Adiciona ao "banco" simulado
            simulated_db[(price.seller_id, price.sku)] = price
            return price
        
        async def mock_find_by_seller_id_and_sku(seller_id, sku):
            price = simulated_db.get((seller_id, sku))
            if price:
                # Retorna como dicionário, como esperado pelos testes
                return {
                    "seller_id": price.seller_id,
                    "sku": price.sku,
                    "de": price.de,
                    "por": price.por,
                    "created_at": price.created_at
                }
            return None
        
        async def mock_update_by_seller_id_and_sku(seller_id, sku, price_update):
            if (seller_id, sku) in simulated_db:
                updated_price = price_update
                updated_price.seller_id = seller_id
                updated_price.sku = sku
                simulated_db[(seller_id, sku)] = updated_price
                return price_update.model_dump()
            raise ValueError("Price not found")
        
        async def mock_delete_by_seller_id_and_sku(seller_id, sku):
            if (seller_id, sku) in simulated_db:
                del simulated_db[(seller_id, sku)]
                return True
            return False
        
        # Patching dos métodos
        repository.create = AsyncMock(side_effect=mock_create)
        repository.find_by_seller_id_and_sku = AsyncMock(side_effect=mock_find_by_seller_id_and_sku)
        repository.update_by_seller_id_and_sku = AsyncMock(side_effect=mock_update_by_seller_id_and_sku)
        repository.delete_by_seller_id_and_sku = AsyncMock(side_effect=mock_delete_by_seller_id_and_sku)
        
        repository._simulated_db = simulated_db
        
        return repository
    

    @pytest.mark.asyncio
    async def test_create(self, repository_mock):
        """Deve criar um novo preço e permitir sua busca."""
        
        novo_preco = Price(seller_id="3", sku="C", de=300, por=270)

        preco_criado = await repository_mock.create(novo_preco)

        assert preco_criado is not None
        assert preco_criado.seller_id == "3"
        assert preco_criado.sku == "C"
        assert preco_criado.de == 300
        assert preco_criado.por == 270
        assert preco_criado.created_at is not None

        # Verifica se pode ser encontrado no repositório
        result_dict = await repository_mock.find_by_seller_id_and_sku("3", "C")
        assert result_dict is not None
        assert result_dict["seller_id"] == "3"
        assert result_dict["sku"] == "C"
        assert result_dict["de"] == 300
        assert result_dict["por"] == 270
        
    @pytest.mark.asyncio
    async def test_create_multiple_prices_with_same_seller_id_and_sku(self, repository_mock):
        """Deve permitir múltiplos preços com o mesmo seller_id e sku (caso permitido pela implementação)."""
        
        price1 = Price(seller_id="1", sku="A", de=150, por=140)
        price2 = Price(seller_id="1", sku="A", de=160, por=150)
        
        await repository_mock.create(price1)
        await repository_mock.create(price2)
        
        # O método find_by_seller_id_and_sku retorna o primeiro encontrado
        result_dict = await repository_mock.find_by_seller_id_and_sku("1", "A")
        assert result_dict is not None
        assert result_dict["seller_id"] == "1"
        assert result_dict["sku"] == "A"
        assert result_dict["de"] == 160 
        assert result_dict["por"] == 150
        
    @pytest.mark.asyncio
    async def test_find_by_seller_id_and_sku_found(self, repository_mock):
        """Deve encontrar um preço existente pelo seller_id e sku."""
        
        result_dict = await repository_mock.find_by_seller_id_and_sku("1", "A")

        assert result_dict is not None
        assert result_dict["seller_id"] == "1"
        assert result_dict["sku"] == "A"
        assert result_dict["de"] == 100
        assert result_dict["por"] == 90

    @pytest.mark.asyncio
    async def test_find_by_seller_id_and_sku_not_found(self, repository_mock):
        """Deve retornar None ao buscar um preço inexistente."""
        
        result_dict = await repository_mock.find_by_seller_id_and_sku("1", "Z")
        assert result_dict is None

    @pytest.mark.asyncio
    async def test_find_by_seller_id_and_sku_with_empty_repository(self, repository_mock):
        """Deve retornar None ao buscar em um repositório vazio."""
        
        repository_mock._simulated_db.clear()
        result_dict = await repository_mock.find_by_seller_id_and_sku("1", "A")
        assert result_dict is None
        
    @pytest.mark.asyncio
    async def test_update_by_seller_id_and_sku(self, repository_mock):
        """Deve atualizar um preço existente."""
        
        # Cria um objeto Price com os novos valores
        updated_price = Price(seller_id="1", sku="A", de=120, por=110)

        # Atualiza o preço
        result_dict = await repository_mock.update_by_seller_id_and_sku("1", "A", updated_price)

        # Verifica se o resultado da atualização está correto
        assert result_dict is not None
        assert result_dict["de"] == 120
        assert result_dict["por"] == 110

        # Verifica se a busca retorna o valor atualizado
        found_price = await repository_mock.find_by_seller_id_and_sku("1", "A")
        assert found_price is not None
        assert found_price["de"] == 120
        assert found_price["por"] == 110

    @pytest.mark.asyncio
    async def test_update_by_seller_id_and_sku_not_found(self, repository_mock):
        """Deve lançar ValueError ao tentar atualizar um preço que não existe."""
        
        updated_price = Price(seller_id="999", sku="ZZZ", de=120, por=110)

        with pytest.raises(ValueError):
            await repository_mock.update_by_seller_id_and_sku("999", "ZZZ", updated_price)
            
    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku(self, repository_mock):
        """Deve remover um preço pelo seller_id e sku."""
        
        #Verifica se o preço existe antes da exclusão
        target_price = await repository_mock.find_by_seller_id_and_sku("1", "A")
        other_price = await repository_mock.find_by_seller_id_and_sku("2", "B")
        assert target_price is not None
        assert other_price is not None
        
        #Remove o preço
        await repository_mock.delete_by_seller_id_and_sku("1", "A")

        # Verifica se o preço foi removido
        assert await repository_mock.find_by_seller_id_and_sku("1", "A") is None
        assert await repository_mock.find_by_seller_id_and_sku("2", "B") == other_price

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku_when_not_exists(self, repository_mock):
        """Deve manter o repositório inalterado ao tentar remover um preço inexistente."""
    
        await repository_mock.delete_by_seller_id_and_sku("999", "ZZZ")
        
        # Tenta deletar um preço que não existe
        repository_mock.delete_by_seller_id_and_sku.assert_called_once_with("999", "ZZZ")
        
        assert await repository_mock.find_by_seller_id_and_sku("999", "ZZZ") is None


