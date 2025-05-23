from unittest.mock import AsyncMock

import pytest

from app.common.exceptions import BadRequestException, NotFoundException
from app.models import Price
from app.repositories import PriceRepository
from app.services import PriceService


class TestPriceService:
    @pytest.fixture
    def repository_mock(self):
        """Cria um mock do repositório para os testes."""
        repository = AsyncMock(spec=PriceRepository)

        # Mock para find_by_seller_id_and_sku
        async def find_by_seller_id_and_sku(seller_id, sku):
            if seller_id == "1" and sku == "A":
                return {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "seller_id": "1",
                    "sku": "A",
                    "preco_de": 100,
                    "preco_por": 90,
                }
            return None

        repository.find_by_seller_id_and_sku.side_effect = find_by_seller_id_and_sku

        # Mock para exists_by_seller_id_and_sku
        async def exists_by_seller_id_and_sku(seller_id, sku):
            return seller_id == "1" and sku == "A"

        repository.exists_by_seller_id_and_sku.side_effect = exists_by_seller_id_and_sku

        # Mock para update_by_seller_id_and_sku
        async def update_by_seller_id_and_sku(seller_id, sku, price_update):
            if seller_id == "1" and sku == "A":
                return {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "seller_id": seller_id,
                    "sku": sku,
                    "preco_de": price_update.preco_de,
                    "preco_por": price_update.preco_por,
                }
            raise ValueError(f"Preço não encontrado para seller_id={seller_id}, sku={sku}")

        repository.update_by_seller_id_and_sku.side_effect = update_by_seller_id_and_sku

        # Mock para create
        async def create(entity):
            return entity

        repository.create.side_effect = create

        # Mock para delete_by_seller_id_and_sku
        async def delete_by_seller_id_and_sku(seller_id, sku):
            return None

        repository.delete_by_seller_id_and_sku.side_effect = delete_by_seller_id_and_sku

        return repository

    @pytest.fixture
    def service(self, repository_mock):
        """Cria o serviço com o repositório mockado."""
        return PriceService(repository=repository_mock)

    @pytest.mark.asyncio
    async def test_get_by_seller_id_and_sku_found(self, service, repository_mock):
        """Deve retornar o preço quando seller_id e sku existem."""
        price = await service.get_by_seller_id_and_sku("1", "A")

        assert price is not None
        assert price.seller_id == "1"
        assert price.sku == "A"
        assert price.preco_de == 100
        assert price.preco_por == 90

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "A")

    @pytest.mark.asyncio
    async def test_get_by_seller_id_and_sku_not_found(self, service, repository_mock):
        """Deve lançar NotFoundException quando não encontrar o preço."""
        with pytest.raises(NotFoundException):
            await service.get_by_seller_id_and_sku("1", "Z")

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "Z")

    @pytest.mark.asyncio
    async def test_create_price_success(self, service, repository_mock):
        """Deve criar um novo preço com sucesso."""
        # Criamos um objeto Price real em vez de um mock
        price_create = Price(seller_id="2", sku="B", preco_de=200, preco_por=180)

        created_price = await service.create_price(price_create)

        assert created_price is not None
        assert created_price.seller_id == "2"
        assert created_price.sku == "B"
        assert created_price.preco_de == 200
        assert created_price.preco_por == 180

        repository_mock.exists_by_seller_id_and_sku.assert_called_once_with("2", "B")
        repository_mock.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_price_already_exists(self, service, repository_mock):
        """Deve lançar BadRequestException ao tentar criar preço já existente."""
        price_create = Price(seller_id="1", sku="A", preco_de=100, preco_por=90)

        with pytest.raises(BadRequestException):
            await service.create_price(price_create)

        repository_mock.exists_by_seller_id_and_sku.assert_called_once_with("1", "A")
        repository_mock.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_price_invalid_price(self, service, repository_mock):
        """Deve lançar BadRequestException ao criar preço com valores inválidos."""
        # Valor negativo para preco_de
        price_create = Price(seller_id="2", sku="B", preco_de=-100, preco_por=90)

        with pytest.raises(BadRequestException) as excinfo:
            await service.create_price(price_create)

        # Verificamos se a exceção menciona 'preco_de' em algum lugar da mensagem
        assert any("preco_de" in str(detail.message) for detail in excinfo.value.details)
        repository_mock.create.assert_not_called()

        # Valor zero para preco_por
        price_create = Price(seller_id="2", sku="B", preco_de=100, preco_por=0)

        with pytest.raises(BadRequestException) as excinfo:
            await service.create_price(price_create)

        # Verificamos se a exceção menciona 'preco_por' em algum lugar da mensagem
        assert any("preco_por" in str(detail.message) for detail in excinfo.value.details)
        repository_mock.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_price_success(self, service, repository_mock):
        """Deve atualizar o preço com sucesso."""
        price_update = Price(seller_id="1", sku="A", preco_de=150, preco_por=120)

        updated_price = await service.update_price("1", "A", price_update)

        assert updated_price is not None
        assert updated_price.seller_id == "1"
        assert updated_price.sku == "A"
        assert updated_price.preco_de == 150
        assert updated_price.preco_por == 120

        repository_mock.exists_by_seller_id_and_sku.assert_called_once_with("1", "A")
        repository_mock.update_by_seller_id_and_sku.assert_called_once_with("1", "A", price_update)

    @pytest.mark.asyncio
    async def test_update_price_not_found(self, service, repository_mock):
        """Deve lançar NotFoundException ao tentar atualizar preço inexistente."""
        # Alteramos o comportamento do mock para este teste específico
        repository_mock.exists_by_seller_id_and_sku.return_value = False

        price_update = Price(seller_id="1", sku="Z", preco_de=150, preco_por=120)

        with pytest.raises(NotFoundException):
            await service.update_price("1", "Z", price_update)

        repository_mock.exists_by_seller_id_and_sku.assert_called_once_with("1", "Z")
        repository_mock.update_by_seller_id_and_sku.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_price_invalid_price(self, service, repository_mock):
        """Deve lançar BadRequestException ao atualizar preço com valores inválidos."""
        # Valor negativo para preco_de
        price_update = Price(seller_id="1", sku="A", preco_de=-150, preco_por=120)

        with pytest.raises(BadRequestException) as excinfo:
            await service.update_price("1", "A", price_update)

        # Verificamos se a exceção menciona 'preco_de' em algum lugar da mensagem
        assert any("preco_de" in str(detail.message) for detail in excinfo.value.details)
        repository_mock.update_by_seller_id_and_sku.assert_not_called()

        # Valor zero para preco_por
        price_update = Price(seller_id="1", sku="A", preco_de=150, preco_por=0)

        with pytest.raises(BadRequestException) as excinfo:
            await service.update_price("1", "A", price_update)

        # Verificamos se a exceção menciona 'preco_por' em algum lugar da mensagem
        assert any("preco_por" in str(detail.message) for detail in excinfo.value.details)
        repository_mock.update_by_seller_id_and_sku.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku_success(self, service, repository_mock):
        """Deve remover o preço com sucesso."""
        await service.delete_by_seller_id_and_sku("1", "A")

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "A")
        repository_mock.delete_by_seller_id_and_sku.assert_called_once_with("1", "A")

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku_not_found(self, service, repository_mock):
        """Deve lançar NotFoundException ao tentar remover preço inexistente."""
        # Alteramos o comportamento do mock para este teste específico
        repository_mock.find_by_seller_id_and_sku.return_value = None

        with pytest.raises(NotFoundException):
            await service.delete_by_seller_id_and_sku("1", "Z")

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with("1", "Z")
        repository_mock.delete_by_seller_id_and_sku.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_price_limite_superior_valores(self, service, repository_mock):
        """Deve criar preço com valores máximos inteiros possíveis."""
        # Valor máximo para int32
        price_create = Price(seller_id="3", sku="C", preco_de=2**31 - 1, preco_por=2**31 - 1)

        # Para este teste, garantimos que o preço não existe
        repository_mock.exists_by_seller_id_and_sku.return_value = False

        created_price = await service.create_price(price_create)

        assert created_price is not None
        assert created_price.preco_de == 2**31 - 1
        assert created_price.preco_por == 2**31 - 1

        repository_mock.exists_by_seller_id_and_sku.assert_called_once_with("3", "C")
        repository_mock.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_price_limite_superior_valores(self, service, repository_mock):
        """Deve atualizar preço com valores máximos inteiros possíveis."""
        price_update = Price(seller_id="1", sku="A", preco_de=2**31 - 1, preco_por=2**31 - 1)

        # Simulando que o preço existe para este teste
        repository_mock.exists_by_seller_id_and_sku.return_value = True

        # Simulando resultado do update
        repository_mock.update_by_seller_id_and_sku.return_value = {
            "id": "00000000-0000-0000-0000-000000000001",
            "seller_id": "1",
            "sku": "A",
            "preco_de": 2**31 - 1,
            "preco_por": 2**31 - 1,
        }

        updated_price = await service.update_price("1", "A", price_update)

        assert updated_price is not None
        assert updated_price.preco_de == 2**31 - 1
        assert updated_price.preco_por == 2**31 - 1

        repository_mock.exists_by_seller_id_and_sku.assert_called_once_with("1", "A")
        repository_mock.update_by_seller_id_and_sku.assert_called_once_with("1", "A", price_update)
