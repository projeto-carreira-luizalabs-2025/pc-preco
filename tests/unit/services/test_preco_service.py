from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from app.common.exceptions import BadRequestException, NotFoundException
from app.models import Preco
from app.repositories import PrecoRepository
from app.services import PrecoService


class TestPrecoService:
    @pytest.fixture
    def repository_mock(self):
        """Cria um mock do repositório para os testes."""
        repository = AsyncMock(spec=PrecoRepository)

        # Comportamento padrão para find_by_seller_id_and_sku
        async def find_by_seller_id_and_sku(seller_id, sku):
            if seller_id == "1" and sku == "A":
                return Preco(
                    id=UUID("00000000-0000-0000-0000-000000000001"), seller_id="1", sku="A", preco_de=100, preco_por=90
                )
            return None

        repository.find_by_seller_id_and_sku.side_effect = find_by_seller_id_and_sku

        # Comportamento padrão para create
        async def create(entity):
            return entity

        repository.create.side_effect = create

        # Comportamento padrão para update
        async def update(entity_id, entity):
            if entity_id == UUID("00000000-0000-0000-0000-000000000001"):
                updated = Preco(
                    id=entity_id, seller_id="1", sku="A", preco_de=entity.preco_de, preco_por=entity.preco_por
                )
                return updated
            raise NotFoundException()

        repository.update.side_effect = update

        return repository

    @pytest.fixture
    def service(self, repository_mock):
        """Cria o serviço com o repositório mockado."""
        return PrecoService(repository=repository_mock)

    @pytest.mark.asyncio
    async def test_find_by_seller_id_and_sku_found(self, service, repository_mock):
        """Deve retornar o preço quando seller_id e sku existem."""
        preco = await service.find_by_seller_id_and_sku("1", "A")

        assert preco is not None
        assert preco.seller_id == "1"
        assert preco.sku == "A"
        assert preco.preco_de == 100
        assert preco.preco_por == 90

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "A")

    @pytest.mark.asyncio
    async def test_find_by_seller_id_and_sku_not_found(self, service, repository_mock):
        """Deve lançar NotFoundException quando não encontrar o preço."""
        with pytest.raises(NotFoundException):
            await service.find_by_seller_id_and_sku("1", "Z")

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "Z")

    @pytest.mark.asyncio
    async def test_create_preco_success(self, service, repository_mock):
        """Deve criar um novo preço com sucesso."""
        preco_create = MagicMock()
        preco_create.seller_id = "2"
        preco_create.sku = "B"
        preco_create.preco_de = 200
        preco_create.preco_por = 180
        preco_create.model_dump.return_value = {"seller_id": "2", "sku": "B", "preco_de": 200, "preco_por": 180}

        repository_mock.find_by_seller_id_and_sku.side_effect = lambda s, k: None

        created_preco = await service.create_preco(preco_create)

        assert created_preco is not None
        assert created_preco.seller_id == "2"
        assert created_preco.sku == "B"
        assert created_preco.preco_de == 200
        assert created_preco.preco_por == 180

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("2", "B")
        repository_mock.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_preco_already_exists(self, service, repository_mock):
        """Deve lançar BadRequestException ao tentar criar preço já existente."""
        preco_create = MagicMock()
        preco_create.seller_id = "1"
        preco_create.sku = "A"
        preco_create.preco_de = 100
        preco_create.preco_por = 90

        with pytest.raises(BadRequestException):
            await service.create_preco(preco_create)

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "A")
        repository_mock.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_preco_invalid_price(self, service, repository_mock):
        """Deve lançar BadRequestException ao criar preço com valores inválidos."""
        preco_create = MagicMock()
        preco_create.seller_id = "2"
        preco_create.sku = "B"
        preco_create.preco_de = -100  # Valor negativo
        preco_create.preco_por = 90

        with pytest.raises(BadRequestException):
            await service.create_preco(preco_create)

        repository_mock.create.assert_not_called()

        preco_create.preco_de = 100
        preco_create.preco_por = 0  # Valor zero

        with pytest.raises(BadRequestException):
            await service.create_preco(preco_create)

        repository_mock.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_preco_success(self, service, repository_mock):
        """Deve atualizar o preço com sucesso."""
        preco_update = MagicMock()
        preco_update.preco_de = 150
        preco_update.preco_por = 120

        updated_preco = await service.update_preco("1", "A", preco_update)

        assert updated_preco is not None
        assert updated_preco.seller_id == "1"
        assert updated_preco.sku == "A"
        assert updated_preco.preco_de == 150
        assert updated_preco.preco_por == 120

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "A")
        repository_mock.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_preco_not_found(self, service, repository_mock):
        """Deve lançar NotFoundException ao tentar atualizar preço inexistente."""
        preco_update = MagicMock()
        preco_update.preco_de = 150
        preco_update.preco_por = 120

        repository_mock.find_by_seller_id_and_sku.side_effect = lambda s, k: None

        with pytest.raises(NotFoundException):
            await service.update_preco("1", "Z", preco_update)

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "Z")
        repository_mock.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_preco_invalid_price(self, service, repository_mock):
        """Deve lançar BadRequestException ao atualizar preço com valores inválidos."""
        preco_update = MagicMock()
        preco_update.preco_de = -150  # Valor negativo
        preco_update.preco_por = 120

        with pytest.raises(BadRequestException):
            await service.update_preco("1", "A", preco_update)

        repository_mock.update.assert_not_called()

        preco_update.preco_de = 150
        preco_update.preco_por = 0  # Valor zero

        with pytest.raises(BadRequestException):
            await service.update_preco("1", "A", preco_update)

        repository_mock.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku_success(self, service, repository_mock):
        """Deve remover o preço com sucesso."""
        await service.delete_by_seller_id_and_sku("1", "A")

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "A")
        repository_mock.delete_by_seller_id_and_sku.assert_called_once_with("1", "A")

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku_not_found(self, service, repository_mock):
        """Deve lançar NotFoundException ao tentar remover preço inexistente."""
        repository_mock.find_by_seller_id_and_sku.side_effect = lambda s, k: None

        with pytest.raises(NotFoundException):
            await service.delete_by_seller_id_and_sku("1", "Z")

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "Z")
        repository_mock.delete_by_seller_id_and_sku.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_preco_limite_superior_valores(self, service, repository_mock):
        """Deve criar preço com valores máximos inteiros possíveis."""
        preco_create = MagicMock()
        preco_create.seller_id = "3"
        preco_create.sku = "C"
        preco_create.preco_de = 2**31 - 1  # Limite superior de int32
        preco_create.preco_por = 2**31 - 1
        preco_create.model_dump.return_value = {
            "seller_id": "3",
            "sku": "C",
            "preco_de": 2**31 - 1,
            "preco_por": 2**31 - 1,
        }
        repository_mock.find_by_seller_id_and_sku.side_effect = lambda s, k: None

        created_preco = await service.create_preco(preco_create)
        assert created_preco.preco_de == 2**31 - 1
        assert created_preco.preco_por == 2**31 - 1

    @pytest.mark.asyncio
    async def test_update_preco_limite_superior_valores(self, service, repository_mock):
        """Deve atualizar preço com valores máximos inteiros possíveis."""
        preco_update = MagicMock()
        preco_update.preco_de = 2**31 - 1
        preco_update.preco_por = 2**31 - 1

        updated_preco = await service.update_preco("1", "A", preco_update)
        assert updated_preco.preco_de == 2**31 - 1
        assert updated_preco.preco_por == 2**31 - 1
