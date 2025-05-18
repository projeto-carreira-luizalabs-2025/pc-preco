from typing import List
from unittest.mock import patch
from uuid import UUID

import pytest

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

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, repository):
        """Deve retornar None ao buscar por ID inexistente."""
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        found_entity = await repository.find_by_id(non_existent_id)
        assert found_entity is None

    @pytest.mark.asyncio
    async def test_update_found(self, repository, test_entities):
        """Deve atualizar uma entidade existente."""
        entity_id = str(test_entities[0].id)
        updated_data = SampleEntity(name="Updated Entity", value=150)

        result = await repository.update(entity_id, updated_data)

        assert result is not None
        assert str(result.id) == entity_id
        assert result.name == "Updated Entity"
        assert result.value == 150
        assert result.updated_at is not None

        # Verifica se a entidade foi realmente atualizada na memória
        found_entity = await repository.find_by_id(entity_id)
        assert found_entity.name == "Updated Entity"
        assert found_entity.value == 150

    @pytest.mark.asyncio
    async def test_update_not_found(self, repository):
        """Deve lançar ValueError ao tentar atualizar entidade inexistente."""
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        updated_data = SampleEntity(name="Updated Entity", value=150)

        with pytest.raises(ValueError):
            await repository.update(non_existent_id, updated_data)

    @pytest.mark.asyncio
    @patch('app.repositories.base.memory_repository.AsyncMemoryRepository.find_by_id')
    async def test_delete_by_id_found(self, mock_find_by_id, repository, test_entities):
        """Deve remover uma entidade existente pelo ID."""
        entity_id = str(test_entities[0].id)

        # Configura o mock para retornar a entidade quando find_by_id for chamado
        mock_find_by_id.return_value = test_entities[0]

        # Guarda o tamanho inicial da memória
        initial_memory_size = len(repository.memory)

        # Executa a operação de delete
        await repository.delete_by_id(entity_id)

        # Verifica se a memória diminuiu
        assert len(repository.memory) == initial_memory_size - 1

    @pytest.mark.asyncio
    @patch('app.repositories.base.memory_repository.AsyncMemoryRepository.find_by_id')
    async def test_delete_by_id_not_found(self, mock_find_by_id, repository):
        """Teste para verificar comportamento ao tentar excluir entidade inexistente."""
        non_existent_id = "00000000-0000-0000-0000-000000000000"

        # Configura o mock para retornar None quando find_by_id for chamado
        mock_find_by_id.return_value = None

        # Guarda o tamanho inicial da memória
        initial_memory = len(repository.memory)

        # Executa a operação de delete
        await repository.delete_by_id(non_existent_id)

        # Verifica se a memória permanece inalterada
        assert len(repository.memory) == initial_memory

    @pytest.mark.asyncio
    async def test_find_with_pagination(self, repository):
        """Deve retornar entidades paginadas corretamente."""
        # Adiciona mais entidades para testar paginação
        for i in range(4, 10):
            entity = SampleEntity(name=f"Entity {i}", value=i * 100)
            await repository.create(entity)

        # Consulta com offset=2, limit=3
        results = await repository.find({}, limit=3, offset=2)

        assert len(results) == 3
        assert results[0].name == "Entity 3"
        assert results[1].name == "Entity 4"
        assert results[2].name == "Entity 5"

    @pytest.mark.asyncio
    async def test_find_with_sorting(self, repository):
        """Deve ordenar entidades corretamente."""
        # Ordenação descendente
        results = await repository.find({}, limit=10, offset=0, sort={"value": -1})

        assert len(results) == 3
        assert results[0].value == 300  # Entity 3
        assert results[1].value == 200  # Entity 2
        assert results[2].value == 100  # Entity 1

        # Ordenação ascendente
        results = await repository.find({}, limit=10, offset=0, sort={"value": 1})

        assert len(results) == 3
        assert results[0].value == 100  # Entity 1
        assert results[1].value == 200  # Entity 2
        assert results[2].value == 300  # Entity 3

    @pytest.mark.asyncio
    async def test_create_entity_with_existing_id(self, repository, test_entities):
        """Deve permitir criar entidade com ID existente, adicionando à memória."""
        entity_with_existing_id = SampleEntity(id=test_entities[0].id, name="Duplicated", value=999)
        created_entity = await repository.create(entity_with_existing_id)

        assert str(created_entity.id) == str(test_entities[0].id)
        assert len(repository.memory) == 4  # Uma nova entidade foi criada

    @pytest.mark.asyncio
    async def test_update_entity_partial_fields(self, repository, test_entities):
        """Deve atualizar apenas os campos fornecidos mantendo os demais."""
        entity_id = str(test_entities[1].id)
        updated_data = SampleEntity(name="Partial Update", value=test_entities[1].value)

        result = await repository.update(entity_id, updated_data)

        assert result.name == "Partial Update"
        assert result.value == 200  # Mantém o valor original

    @pytest.mark.asyncio
    async def test_find_with_empty_memory(self):
        """Deve retornar lista vazia ao buscar em repositório vazio."""
        empty_repo = AsyncMemoryRepository[SampleEntity, str](key_name="id", model_class=SampleEntity)
        results = await empty_repo.find({}, limit=10, offset=0)
        assert results == []

    @pytest.mark.asyncio
    async def test_find_with_offset_beyond_length(self, repository):
        """Deve retornar lista vazia se offset for maior que o número de entidades."""
        results = await repository.find({}, limit=5, offset=10)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_find_with_limit_zero(self, repository):
        """Deve retornar lista vazia se limit for zero."""
        results = await repository.find({}, limit=0, offset=0)
        assert len(results) == 0
