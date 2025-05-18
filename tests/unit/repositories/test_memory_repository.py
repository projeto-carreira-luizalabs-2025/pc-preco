from typing import List

import pytest

from app.models.base import PersistableEntity
from app.repositories.base import AsyncMemoryRepository


class SampleEntity(PersistableEntity):
    name: str
    value: int


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
        repo = AsyncMemoryRepository[SampleEntity, str](key_name="id", model_class=SampleEntity)
        # Preenche a memória manualmente
        for entity in test_entities:
            entity_dict = entity.model_dump(by_alias=True)
            # Garante que o ID esteja no formato correto para comparações
            entity_dict["id"] = str(entity.id)
            repo.memory.append(entity_dict)
        return repo

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
        entity_id = str(test_entities[0].id)
        found_entity = await repository.find_by_id(entity_id)

        assert found_entity is not None
        assert str(found_entity.id) == entity_id
        assert found_entity.name == "Entity 1"
        assert found_entity.value == 100
