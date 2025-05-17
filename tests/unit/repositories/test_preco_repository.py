import pytest

from app.models import Preco
from app.repositories import PrecoRepository


class TestPrecoRepository:
    @pytest.fixture
    def repository(self):
        """Cria um repositório com dados de teste."""
        return PrecoRepository(
            memory=[
                Preco(seller_id="1", sku="A", preco_de=100, preco_por=90),
                Preco(seller_id="2", sku="B", preco_de=200, preco_por=180),
            ]
        )

    @pytest.mark.asyncio
    async def test_find_by_seller_id_and_sku_found(self, repository):
        """Deve encontrar um preço existente pelo seller_id e sku."""
        preco = await repository.find_by_seller_id_and_sku("1", "A")

        assert preco is not None
        assert preco.seller_id == "1"
        assert preco.sku == "A"
        assert preco.preco_de == 100
        assert preco.preco_por == 90

    @pytest.mark.asyncio
    async def test_find_by_seller_id_and_sku_not_found(self, repository):
        """Deve retornar None ao buscar um preço inexistente."""
        preco = await repository.find_by_seller_id_and_sku("1", "Z")

        assert preco is None

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku(self, repository):
        """Deve remover um preço pelo seller_id e sku."""
        # Verifica se o preço existe antes da exclusão
        preco = await repository.find_by_seller_id_and_sku("1", "A")
        assert preco is not None

        # Remove o preço
        await repository.delete_by_seller_id_and_sku("1", "A")

        # Verifica se o preço não existe mais
        preco = await repository.find_by_seller_id_and_sku("1", "A")
        assert preco is None

        # Verifica se outros preços ainda existem
        preco = await repository.find_by_seller_id_and_sku("2", "B")
        assert preco is not None

    @pytest.mark.asyncio
    async def test_create(self, repository):
        """Deve criar um novo preço e permitir sua busca."""
        novo_preco = Preco(seller_id="3", sku="C", preco_de=300, preco_por=270)

        preco_criado = await repository.create(novo_preco)

        assert preco_criado is not None
        assert preco_criado.seller_id == "3"
        assert preco_criado.sku == "C"
        assert preco_criado.preco_de == 300
        assert preco_criado.preco_por == 270
        assert preco_criado.created_at is not None

        # Verifica se pode ser encontrado no repositório
        preco_encontrado = await repository.find_by_seller_id_and_sku("3", "C")
        assert preco_encontrado is not None
        assert preco_encontrado.seller_id == "3"
        assert preco_encontrado.sku == "C"

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku_when_not_exists(self, repository):
        """Deve manter o repositório inalterado ao tentar remover um preço inexistente."""
        await repository.delete_by_seller_id_and_sku("999", "ZZZ")
        # Nenhum preço deve ser removido
        assert len(repository.memory) == 2

    @pytest.mark.asyncio
    async def test_find_by_seller_id_and_sku_with_empty_repository(self):
        """Deve retornar None ao buscar em um repositório vazio."""
        repo = PrecoRepository(memory=[])
        preco = await repo.find_by_seller_id_and_sku("1", "A")
        assert preco is None

    @pytest.mark.asyncio
    async def test_create_multiple_precos_with_same_seller_id_and_sku(self, repository):
        """Deve permitir múltiplos preços com o mesmo seller_id e sku (caso permitido pela implementação)."""
        preco1 = Preco(seller_id="1", sku="A", preco_de=150, preco_por=140)
        preco2 = Preco(seller_id="1", sku="A", preco_de=160, preco_por=150)
        await repository.create(preco1)
        await repository.create(preco2)
        # O método find_by_seller_id_and_sku retorna o primeiro encontrado
        preco_encontrado = await repository.find_by_seller_id_and_sku("1", "A")
        assert preco_encontrado is not None
        assert preco_encontrado.seller_id == "1"
        assert preco_encontrado.sku == "A"
