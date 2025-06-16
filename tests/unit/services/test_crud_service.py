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
            if seller_id == "1" and sku == "A":
                if isinstance(entity, dict):
                    name = entity.get("name", "Default Name")
                    value = entity.get("value", 0)
                else:
                    name = entity.name
                    value = entity.value
                return SampleEntity(id=None, name=entity.name, value=entity.value)
            return None
        
        repository.update_by_seller_id_and_sku.side_effect = update_by_seller_id_and_sku

        async def patch_by_seller_id_and_sku(seller_id, sku, patch_data):
            if seller_id == "test_seller" and sku == "test_sku":
                return SampleEntity(
                    id=None, 
                    name=patch_data.get("name", "Default"), 
                    value=patch_data.get("value", 0)
                )
            return None
        
        repository.patch_by_seller_id_and_sku.side_effect = patch_by_seller_id_and_sku

        async def delete_by_seller_id_and_sku(seller_id, sku):
            if seller_id == "test_seller" and sku == "test_sku":
                pass
                
            return None
        
        repository.delete_by_seller_id_and_sku.side_effect = delete_by_seller_id_and_sku

        return repository
    
    @pytest.fixture
    def service(self, repository_mock):
        """Cria um serviço com o repositório mock."""
        return CrudService[SampleEntity, UUID](repository=repository_mock)

    @pytest.mark.asyncio
    async def test_create(self, service, repository_mock):
        """Deve criar uma entidade corretamente."""
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
    async def test_find_by_seller_id_and_sku_not_found_raises_exception(self, service, repository_mock):
        """Deve lançar NotFoundException quando a entidade não for encontrada."""
        seller_id = "1"
        sku = "INEXISTENTE"
        
        with pytest.raises(NotFoundException):
            await service.find_by_seller_id_and_sku(seller_id, sku)

        repository_mock.find_by_seller_id_and_sku.assert_called_once_with(seller_id, sku)
         
    @pytest.mark.asyncio
    async def test_find_by_seller_id_and_sku_not_found_with_no_exception(self, service, repository_mock):
        """Deve retornar None ao buscar seller_id + sku inexistente com can_raise_exception=False."""
        
        seller_id = "1"
        sku = "INEXISTENTE"
        
        found_entity = await service.find_by_seller_id_and_sku(seller_id , sku, can_raise_exception=False)
        
        assert found_entity is None
        repository_mock.find_by_seller_id_and_sku.assert_called_once_with(seller_id, sku)

    @pytest.mark.asyncio
    async def test_find_with_empty_filters(self, service, repository_mock):
        """Deve chamar o repositório com filtros vazios."""
        paginator = MagicMock(spec=Paginator)
        paginator.limit = 10
        paginator.offset = 0
        paginator.get_sort_order.return_value = None

        await service.find(paginator, {})

        repository_mock.find.assert_called_once_with(filters={}, limit=10, offset=0, sort=None)

    @pytest.mark.asyncio
    async def test_find_with_complex_sort(self, service, repository_mock):
        """Deve processar corretamente ordenação complexa."""
        paginator = MagicMock(spec=Paginator)
        paginator.limit = 20
        paginator.offset = 10
        paginator.get_sort_order.return_value = {"name": 1, "value": -1}

        await service.find(paginator, {"status": "active"})

        repository_mock.find.assert_called_once_with(
            filters={"status": "active"}, limit=20, offset=10, sort={"name": 1, "value": -1}
        )

    @pytest.mark.asyncio
    async def test_find_with_limit_zero(self, service, repository_mock):
        """Deve aceitar limite zero e passar para o repositório."""
        paginator = MagicMock(spec=Paginator)
        paginator.limit = 0
        paginator.offset = 0
        paginator.get_sort_order.return_value = None

        await service.find(paginator, {})

        repository_mock.find.assert_called_once_with(filters={}, limit=0, offset=0, sort=None)

    @pytest.mark.asyncio
    async def test_update_with_partial_data(self, service, repository_mock):
        """Deve atualizar entidade com dados parciais."""
        seller_id = "test_seller"
        sku = "test_sku"
        partial_data = {"name": "Updated Name Only"}

        await service.update_by_seller_id_and_sku(seller_id, sku, partial_data)

        repository_mock.update_by_seller_id_and_sku.assert_called_once_with(seller_id, sku, partial_data)

    @pytest.mark.asyncio
    async def test_find(self, service, repository_mock):
        """Deve retornar uma lista de entidades ao buscar com filtros e paginação."""
        paginator = MagicMock(spec=Paginator)
        paginator.limit = 10
        paginator.offset = 0
        paginator.get_sort_order.return_value = {"name": 1}

        filters = {"name": "Test"}

        results = await service.find(paginator, filters)

        assert len(results) == 2
        assert results[0].name == "Test Entity 1"
        assert results[1].name == "Test Entity 2"

        repository_mock.find.assert_called_once_with(
            filters=filters, limit=paginator.limit, offset=paginator.offset, sort=paginator.get_sort_order()
        )

    @pytest.mark.asyncio
    async def test_find_empty_result(self, service, repository_mock):
        """Deve retornar lista vazia quando não houver resultados."""
        repository_mock.find.side_effect = lambda filters, limit, offset, sort: []
        paginator = MagicMock(spec=Paginator)
        paginator.limit = 10
        paginator.offset = 0
        paginator.get_sort_order.return_value = None
        filters = {}
        results = await service.find(paginator, filters)
        assert results == []

    @pytest.mark.asyncio
    async def test_update_by_seller_id_and_sku(self, service, repository_mock):
        """Deve atualizar uma entidade existente."""
        seller_id = "1"
        sku = "A"
        entity_update_data = SampleEntity(name="Updated Entity", value=150)

        updated_entity = await service.update_by_seller_id_and_sku(seller_id, sku, entity_update_data)

        assert updated_entity is not None
        assert updated_entity.name == "Updated Entity"
        assert updated_entity.value == 150
        
        repository_mock.update_by_seller_id_and_sku.assert_called_once_with(seller_id, sku, entity_update_data)

    @pytest.mark.asyncio
    async def test_update_by_seller_id_and_sku_not_found(self, service, repository_mock):
        """Deve retornar None ao tentar atualizar uma entidade inexistente."""
        seller_id = "1"
        sku = "INEXISTENTE"
        entity_update_data = SampleEntity(name="Does Not Exist", value=0)

        updated_entity = await service.update_by_seller_id_and_sku(seller_id, sku, entity_update_data)

        assert updated_entity is None
        repository_mock.update_by_seller_id_and_sku.assert_called_once_with(seller_id, sku, entity_update_data)

    @pytest.mark.asyncio
    async def test_delete_by_seller_id_and_sku(self, service, repository_mock):
        """Deve deletar uma entidade pelo seller_id e sku."""
        seller_id = "1"
        sku = "A"
        
        await service.delete_by_seller_id_and_sku(seller_id, sku)
        
        repository_mock.delete_by_seller_id_and_sku.assert_called_once_with(seller_id, sku)

    @pytest.mark.asyncio
    async def test_delete_by_id_not_found(self, service, repository_mock):
        """Deve não lançar erro ao deletar um seller_id + sku inexistente."""
        seller_id = "1"
        sku = "A"
        
        # Simula que nenhuma entidade foi encontrada/deletada
        repository_mock.delete_by_seller_id_and_sku.return_value = None
        
        # Executa o método - não deve lançar exceção
        deleted_entity = await service.delete_by_seller_id_and_sku(seller_id, sku)
         
        repository_mock.delete_by_seller_id_and_sku.assert_called_once_with(seller_id, sku)
        
        assert deleted_entity is None
         
    def test_context_property(self, service):
        """Deve retornar None para a propriedade context."""
        assert service.context is None

    def test_author_property(self, service):
        """Deve retornar None para a propriedade author."""
        assert service.author is None
