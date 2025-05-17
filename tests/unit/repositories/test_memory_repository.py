from typing import List
from uuid import UUID

import pytest

from app.common.exceptions import NotFoundException
from app.models.base import PersistableEntity
from app.repositories.base import AsyncMemoryRepository


class SampleEntity(PersistableEntity):
    name: str
    value: int

    @property
    def identity(self) -> UUID:
        """Propriedade para compatibilidade com o repositório que espera um atributo identity."""
        return self.id


class TestAsyncMemoryRepository:
    @pytest.fixture
    def test_entities(self) -> List[SampleEntity]:
        """Cria entidades de teste para os testes do repositório."""
        return [
            SampleEntity(name="Entity 1", value=100),
            SampleEntity(name="Entity 2", value=200),
            SampleEntity(name="Entity 3", value=300),
        ]

    @pytest.fixture
    def repository(self, test_entities):
        """Cria um repositório com dados de teste."""
        return AsyncMemoryRepository[SampleEntity, UUID](memory=test_entities)

    @pytest.mark.asyncio
    async def test_create(self, repository):
        """Deve criar uma nova entidade e adicioná-la à memória."""
        entity = SampleEntity(name="New Entity", value=400)
        created_entity = await repository.create(entity)
        assert created_entity is not None
        assert created_entity.name == "New Entity"
        assert created_entity.value == 400
        assert created_entity.created_at is not None
        assert len(repository.memory) == 4

    @pytest.mark.asyncio
    async def test_find_by_id_found(self, repository, test_entities):
        """Deve encontrar uma entidade pelo ID quando ela existe."""
        entity_id = test_entities[0].id
        found_entity = await repository.find_by_id(entity_id)
        assert found_entity is not None
        assert found_entity.id == entity_id
        assert found_entity.name == "Entity 1"
        assert found_entity.value == 100

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, repository):
        """Deve lançar NotFoundException ao buscar por ID inexistente."""
        non_existent_id = UUID("00000000-0000-0000-0000-000000000000")
        with pytest.raises(NotFoundException):
            await repository.find_by_id(non_existent_id)

    @pytest.mark.asyncio
    async def test_update_found(self, repository, test_entities):
        """Deve atualizar uma entidade existente."""
        entity_id = test_entities[0].id
        updated_data = SampleEntity(name="Updated Entity", value=150)
        result = await repository.update(entity_id, updated_data)
        assert result is not None
        assert result.id == entity_id
        assert result.name == "Updated Entity"
        assert result.value == 150
        assert result.updated_at is not None
        found_entity = await repository.find_by_id(entity_id)
        assert found_entity.name == "Updated Entity"
        assert found_entity.value == 150

    @pytest.mark.asyncio
    async def test_update_not_found(self, repository):
        """Deve lançar NotFoundException ao tentar atualizar entidade inexistente."""
        non_existent_id = UUID("00000000-0000-0000-0000-000000000000")
        updated_data = SampleEntity(name="Updated Entity", value=150)
        with pytest.raises(NotFoundException):
            await repository.update(non_existent_id, updated_data)

    @pytest.mark.asyncio
    async def test_delete_by_id_found(self, repository, test_entities):
        """Deve remover uma entidade existente pelo ID."""
        entity_id = test_entities[0].id
        found_entity = await repository.find_by_id(entity_id)
        assert found_entity is not None
        await repository.delete_by_id(entity_id)
        with pytest.raises(NotFoundException):
            await repository.find_by_id(entity_id)
        assert len(repository.memory) == 2

    @pytest.mark.asyncio
    async def test_delete_by_id_not_found(self, repository):
        """Deve lançar NotFoundException ao tentar remover entidade inexistente."""
        non_existent_id = UUID("00000000-0000-0000-0000-000000000000")
        with pytest.raises(NotFoundException):
            await repository.delete_by_id(non_existent_id)

    @pytest.mark.asyncio
    async def test_find_with_pagination(self, repository):
        """Deve retornar entidades paginadas corretamente."""
        for i in range(4, 10):
            await repository.create(SampleEntity(name=f"Entity {i}", value=i * 100))
        results = await repository.find({}, limit=3, offset=2)
        assert len(results) == 3
        assert results[0].name == "Entity 3"
        assert results[1].name == "Entity 4"
        assert results[2].name == "Entity 5"

    @pytest.mark.asyncio
    async def test_find_with_sorting(self, repository):
        """Deve ordenar entidades corretamente."""
        results = await repository.find({}, limit=10, offset=0, sort={"value": -1})
        assert len(results) == 3
        assert results[0].value == 300
        assert results[1].value == 200
        assert results[2].value == 100
        results = await repository.find({}, limit=10, offset=0, sort={"value": 1})
        assert len(results) == 3
        assert results[0].value == 100
        assert results[1].value == 200
        assert results[2].value == 300

    @pytest.mark.asyncio
    async def test_create_entity_with_existing_id(self, repository, test_entities):
        """Deve permitir criar entidade com ID já existente (simula sobrescrita de ID)."""
        entity_with_existing_id = SampleEntity(id=test_entities[0].id, name="Duplicated", value=999)
        created_entity = await repository.create(entity_with_existing_id)
        assert created_entity.id == test_entities[0].id
        assert len(repository.memory) == 4

    @pytest.mark.asyncio
    async def test_update_entity_partial_fields(self, repository, test_entities):
        """Deve atualizar apenas os campos fornecidos mantendo os demais."""
        entity_id = test_entities[1].id
        updated_data = SampleEntity(name="Partial Update", value=test_entities[1].value)
        result = await repository.update(entity_id, updated_data)
        assert result.name == "Partial Update"
        assert result.value == 200

    @pytest.mark.asyncio
    async def test_find_with_empty_memory(self):
        """Deve retornar lista vazia ao buscar em repositório vazio."""
        repository = AsyncMemoryRepository[SampleEntity, UUID](memory=[])
        results = await repository.find({}, limit=10, offset=0)
        assert results == []

    @pytest.mark.asyncio
    async def test_find_with_offset_beyond_length(self, repository):
        """Deve retornar lista vazia se offset for maior que o número de entidades."""
        results = await repository.find({}, limit=5, offset=10)
        assert results == []

    @pytest.mark.asyncio
    async def test_find_with_limit_zero(self, repository):
        """Deve retornar lista vazia se limit for zero."""
        results = await repository.find({}, limit=0, offset=0)
        assert results == []
