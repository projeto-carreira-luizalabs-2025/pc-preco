import pytest

from app.models import Price
from tests.factories.price_repository_mock_factory import PriceRepositoryMockFactory


@pytest.mark.asyncio
class TestPrecoRepository:

    @pytest.fixture
    def repository_mock(self):
        """Repositório com dados simulados."""
        return PriceRepositoryMockFactory.create_mock_repository()

    @pytest.fixture
    def empty_repository_mock(self):
        """Repositório vazio."""
        return PriceRepositoryMockFactory.create_empty_mock_repository()

    @pytest.fixture
    def custom_repository_mock(self):
        """Repositório com dados customizados."""
        custom_prices = [
            Price(seller_id="custom1", sku="X", de=500, por=450),
            Price(seller_id="custom2", sku="Y", de=600, por=550),
        ]
        return PriceRepositoryMockFactory.create_mock_repository_with_custom_data(custom_prices)

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
        result_obj = await repository_mock.find_by_seller_id_and_sku("3", "C")
        assert result_obj is not None
        assert result_obj.seller_id == "3"
        assert result_obj.sku == "C"
        assert result_obj.de == 300
        assert result_obj.por == 270

    async def test_create_multiple_prices_with_same_seller_id_and_sku(self, repository_mock):
        """Deve permitir múltiplos preços com o mesmo seller_id e sku (caso permitido pela implementação)."""
        price1 = Price(seller_id="1", sku="A", de=150, por=140)
        price2 = Price(seller_id="1", sku="A", de=160, por=150)

        await repository_mock.create(price1)
        await repository_mock.create(price2)

        # O método find_by_seller_id_and_sku retorna o primeiro encontrado
        result_obj = await repository_mock.find_by_seller_id_and_sku("1", "A")
        assert result_obj is not None
        assert result_obj.seller_id == "1"
        assert result_obj.sku == "A"
        assert result_obj.de == 160
        assert result_obj.por == 150

    async def test_find_by_seller_id_and_sku_found(self, repository_mock):
        """Deve encontrar um preço existente pelo seller_id e sku."""
        result_obj = await repository_mock.find_by_seller_id_and_sku("1", "A")

        assert result_obj is not None
        assert result_obj.seller_id == "1"
        assert result_obj.sku == "A"
        assert result_obj.de == 100
        assert result_obj.por == 90

    async def test_find_by_seller_id_and_sku_not_found(self, repository_mock):
        """Deve retornar None ao buscar um preço inexistente."""
        return_obj = await repository_mock.find_by_seller_id_and_sku("1", "Z")
        assert return_obj is None

    async def test_find_by_seller_id_and_sku_with_empty_repository(self, empty_repository_mock):
        """Deve retornar None ao buscar em um repositório vazio."""
        return_obj = await empty_repository_mock.find_by_seller_id_and_sku("1", "A")
        assert return_obj is None

    async def test_update_by_seller_id_and_sku(self, repository_mock):
        """Deve atualizar um preço existente."""
        updated_price = Price(seller_id="1", sku="A", de=120, por=110)
        return_obj = await repository_mock.update_by_seller_id_and_sku("1", "A", updated_price)

        # Verifica se o resultado da atualização está correto
        assert return_obj is not None
        assert return_obj.de == 120
        assert return_obj.por == 110

        # Verifica se a busca retorna o valor atualizado
        found_price = await repository_mock.find_by_seller_id_and_sku("1", "A")
        assert found_price is not None
        assert found_price.de == 120
        assert found_price.por == 110

    async def test_update_by_seller_id_and_sku_not_found(self, repository_mock):
        """Deve lançar ValueError ao tentar atualizar um preço que não existe."""
        updated_price = Price(seller_id="999", sku="ZZZ", de=120, por=110)

        with pytest.raises(ValueError):
            await repository_mock.update_by_seller_id_and_sku("999", "ZZZ", updated_price)

    async def test_delete_by_seller_id_and_sku(self, repository_mock):
        """Deve remover um preço pelo seller_id e sku."""
        # Verifica se o preço existe antes da exclusão
        target_price = await repository_mock.find_by_seller_id_and_sku("1", "A")
        assert target_price is not None

        # Remove o preço
        await repository_mock.delete_by_seller_id_and_sku("1", "A")

        # Verifica se o preço foi removido
        assert await repository_mock.find_by_seller_id_and_sku("1", "A") is None

    async def test_delete_by_seller_id_and_sku_when_not_exists(self, repository_mock):
        """Deve manter o repositório inalterado ao tentar remover um preço inexistente."""
        await repository_mock.delete_by_seller_id_and_sku("999", "ZZZ")

        # Tenta deletar um preço que não existe
        repository_mock.delete_by_seller_id_and_sku.assert_called_once_with("999", "ZZZ")
        assert await repository_mock.find_by_seller_id_and_sku("999", "ZZZ") is None
