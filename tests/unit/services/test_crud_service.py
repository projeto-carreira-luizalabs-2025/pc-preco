from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from app.api.common.schemas import Paginator
from app.common.exceptions import NotFoundException
from app.models.base import PersistableEntity
from app.repositories.base import AsyncCrudRepository
from app.services.base import CrudService


class SampleEntity(PersistableEntity):
    name: str
    value: int


class TestCrudService:

    @pytest.fixture
    def repository_mock(self):
        """Cria um repositório mock para os testes."""
        repository = AsyncMock(spec=AsyncCrudRepository)

        async def create(entity):
            return entity

        repository.create.side_effect = create

        async def find(filters, limit, offset, sort):
            return [
                SampleEntity(id=UUID("00000000-0000-0000-0000-000000000001"), name="Test Entity 1", value=100),
                SampleEntity(id=UUID("00000000-0000-0000-0000-000000000002"), name="Test Entity 2", value=200),
            ]

        repository.find.side_effect = find

        async def find_by_seller_id_and_sku(seller_id, sku):
            if seller_id == "1" and sku == "A":
                return SampleEntity(id=None, name="Test Entity", value=100)
            return None

        repository.find_by_seller_id_and_sku.side_effect = find_by_seller_id_and_sku

        async def update_by_seller_id_and_sku(seller_id, sku, entity):
            if seller_id == "1" and sku == "A" or (seller_id == "test_seller" and sku == "test_sku"):
                return SampleEntity(id=None, name=entity.name, value=entity.value)
            return None

        repository.update_by_seller_id_and_sku.side_effect = update_by_seller_id_and_sku

        async def delete_by_seller_id_and_sku(seller_id, sku):
            if seller_id == "test_seller" and sku == "test_sku":
                return True
            return None

        repository.delete_by_seller_id_and_sku.side_effect = delete_by_seller_id_and_sku

        return repository

    @pytest.fixture
    def service(self, repository_mock):
        """Cria um serviço com o repositório mock."""
        return CrudService[SampleEntity](repository=repository_mock)

    @pytest.mark.asyncio
    async def test_create(self, service, repository_mock):
        entity_data = SampleEntity(name="New Entity", value=300)
        created_entity = await service.create(entity_data)
        assert created_entity is not None
        assert created_entity.name == "New Entity"
        assert created_entity.value == 300
        repository_mock.create.assert_called_once_with(entity_data)

    @pytest.mark.asyncio
    async def test_find_by_seller_id_and_sku(self, service, repository_mock):
        seller_id = "1"
        sku = "A"
        found_entity = await service.find_by_seller_id_and_sku(seller_id, sku)
        assert found_entity is not None
        assert found_entity.name == "Test Entity"
        assert found_entity.value == 100
        repository_mock.find_by_seller_id_and_sku.assert_called_once_with(seller_id, sku)

    @pytest.mark.asyncio
    async def test_update_by_seller_id_and_sku(self, service, repository_mock):
        seller_id = "test_seller"
        sku = "test_sku"
        entity = SampleEntity(name="Updated Name", value=888)
        updated_entity = await service.update_by_seller_id_and_sku(seller_id, sku, entity)
        assert updated_entity is not None
        assert updated_entity.name == "Updated Name"
        assert updated_entity.value == 888
        repository_mock.update_by_seller_id_and_sku.assert_called_once_with(seller_id, sku, entity)

    @pytest.mark.asyncio
    async def test_update_by_seller_id_and_sku_not_found(self, service, repository_mock):
        seller_id = "not_found"
        sku = "not_found"
        entity = SampleEntity(name="Does Not Exist", value=0)
        updated_entity = await service.update_by_seller_id_and_sku(seller_id, sku, entity)
        assert updated_entity is None
        repository_mock.update_by_seller_id_and_sku.assert_called_once_with(seller_id, sku, entity)

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku(self, service, repository_mock):
        seller_id = "test_seller"
        sku = "test_sku"
        result = await service.delete_by_seller_id_and_sku(seller_id, sku)
        assert result is True
        repository_mock.delete_by_seller_id_and_sku.assert_called_once_with(seller_id, sku)

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku_not_found(self, service, repository_mock):
        seller_id = "not_found"
        sku = "not_found"
        result = await service.delete_by_seller_id_and_sku(seller_id, sku)
        assert result is None
        repository_mock.delete_by_seller_id_and_sku.assert_called_once_with(seller_id, sku)
