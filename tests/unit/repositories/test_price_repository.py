import pytest

from app.models import Price
from app.repositories import PriceRepository


class TestPrecoRepository:
    @pytest.fixture
    def repository(self):
        """Cria um repositório com dados de teste."""
        # Convertemos os objetos Price para dicionários, como esperado pelo repositório
        return PriceRepository(
            memory=[
                {"seller_id": "1", "sku": "A", "de": 100, "por": 90},
                {"seller_id": "2", "sku": "B", "de": 200, "por": 180},
            ]
        )

    @pytest.mark.asyncio
    async def test_find_by_seller_id_and_sku_found(self, repository):
        """Deve encontrar um preço existente pelo seller_id e sku."""
        result_dict = await repository.find_by_seller_id_and_sku("1", "A")

        assert result_dict is not None
        assert result_dict["seller_id"] == "1"
        assert result_dict["sku"] == "A"
        assert result_dict["de"] == 100
        assert result_dict["por"] == 90

    @pytest.mark.asyncio
    async def test_find_by_seller_id_and_sku_not_found(self, repository):
        """Deve retornar None ao buscar um preço inexistente."""
        result_dict = await repository.find_by_seller_id_and_sku("1", "Z")

        assert result_dict is None

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku(self, repository):
        """Deve remover um preço pelo seller_id e sku."""
        # Verifica se o preço existe antes da exclusão
        result_dict = await repository.find_by_seller_id_and_sku("1", "A")
        assert result_dict is not None

        # Remove o preço
        await repository.delete_by_seller_id_and_sku("1", "A")

        # Verifica se o preço não existe mais
        result_dict = await repository.find_by_seller_id_and_sku("1", "A")
        assert result_dict is None

        # Verifica se outros preços ainda existem
        result_dict = await repository.find_by_seller_id_and_sku("2", "B")
        assert result_dict is not None

    @pytest.mark.asyncio
    async def test_create(self, repository):
        """Deve criar um novo preço e permitir sua busca."""
        novo_preco = Price(seller_id="3", sku="C", de=300, por=270)

        preco_criado = await repository.create(novo_preco)

        assert preco_criado is not None
        assert preco_criado.seller_id == "3"
        assert preco_criado.sku == "C"
        assert preco_criado.de == 300
        assert preco_criado.por == 270
        assert preco_criado.created_at is not None

        # Verifica se pode ser encontrado no repositório
        result_dict = await repository.find_by_seller_id_and_sku("3", "C")
        assert result_dict is not None
        assert result_dict["seller_id"] == "3"
        assert result_dict["sku"] == "C"

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku_when_not_exists(self, repository):
        """Deve manter o repositório inalterado ao tentar remover um preço inexistente."""
        initial_count = len(repository.memory)
        await repository.delete_by_seller_id_and_sku("999", "ZZZ")
        # Nenhum preço deve ser removido
        assert len(repository.memory) == initial_count

    @pytest.mark.asyncio
    async def test_find_by_seller_id_and_sku_with_empty_repository(self):
        """Deve retornar None ao buscar em um repositório vazio."""
        repo = PriceRepository(memory=[])
        result_dict = await repo.find_by_seller_id_and_sku("1", "A")
        assert result_dict is None

    @pytest.mark.asyncio
    async def test_create_multiple_precos_with_same_seller_id_and_sku(self, repository):
        """Deve permitir múltiplos preços com o mesmo seller_id e sku (caso permitido pela implementação)."""
        preco1 = Price(seller_id="1", sku="A", de=150, por=140)
        preco2 = Price(seller_id="1", sku="A", de=160, por=150)
        await repository.create(preco1)
        await repository.create(preco2)
        # O método find_by_seller_id_and_sku retorna o primeiro encontrado
        result_dict = await repository.find_by_seller_id_and_sku("1", "A")
        assert result_dict is not None
        assert result_dict["seller_id"] == "1"
        assert result_dict["sku"] == "A"

    @pytest.mark.asyncio
    async def test_update_by_seller_id_and_sku(self, repository):
        """Deve atualizar um preço existente."""
        # Cria um objeto Price com os novos valores
        updated_price = Price(seller_id="1", sku="A", de=120, por=110)

        # Atualiza o preço
        result_dict = await repository.update_by_seller_id_and_sku("1", "A", updated_price)

        # Verifica se o resultado da atualização está correto
        assert result_dict is not None
        assert result_dict["de"] == 120
        assert result_dict["por"] == 110

        # Verifica se a busca retorna o valor atualizado
        found_price = await repository.find_by_seller_id_and_sku("1", "A")
        assert found_price is not None
        assert found_price["de"] == 120
        assert found_price["por"] == 110

    @pytest.mark.asyncio
    async def test_update_by_seller_id_and_sku_not_found(self, repository):
        """Deve lançar ValueError ao tentar atualizar um preço que não existe."""
        updated_price = Price(seller_id="999", sku="ZZZ", de=120, por=110)

        with pytest.raises(ValueError):
            await repository.update_by_seller_id_and_sku("999", "ZZZ", updated_price)
