from typing import Any, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel

from app.common.datetime import utcnow
from app.common.exceptions import NotFoundException

from .async_crud_repository import AsyncCrudRepository

T = TypeVar("T", bound=BaseModel)
ID = TypeVar("ID", bound=int | str)


class AsyncMemoryRepository(AsyncCrudRepository[T, ID], Generic[T, ID]):

    def __init__(self, key_name: str, model_class: Type[T]):
        super().__init__()
        self.key_name = key_name
        self.memory: list[dict] = []
        self.model_class = model_class
        # Deveria passar dinamco

    async def create(self, entity: T) -> T:
        entity_dict = entity.model_dump(by_alias=True)
        entity_dict["created_at"] = utcnow()

        self.memory.append(entity_dict)

        return entity

    async def find_by_id(self, entity_id: ID) -> Optional[T]:
        # XXX Lembrar que elementos da memória são dicionionários
        result = next((r for r in self.memory if r.get(self.key_name) == entity_id), None)
        if result is not None:
            result = self.model_class(**result)
        return result

    @staticmethod
    def _can_filter(data: T, filters: dict | None) -> bool:
        filters = filters or {}

        for key, value in filters.items():
            if value is not None and data.get(key) != value:
                return False
        return True

    async def find(self, filters: dict, limit: int = 10, offset: int = 0, sort: Optional[dict] = None) -> List[T]:
        filtered_list = [data for data in self.memory if self._can_filter(data, filters)]

        # XXX TODO Falta ordenar
        # Ordenação
        if sort:
            # Tirar os espaços de chaves do sort
            stripped_sort = {key.strip(): value for key, value in sort.items()}

            for field, direction in reversed(list(stripped_sort.items())):
                reverse = direction == -1  # Reverse é true caso for em ordem descendente
                filtered_list = sorted(filtered_list, key=lambda x: getattr(x, field, None), reverse=reverse)

        # Paginação
        paginated_list = filtered_list[offset : offset + limit]

        entities = []
        for document in paginated_list:
            entities.append(document)
        return entities

        result_list = [self.model_class(**register) for register in filtered_list]
        return result_list

    async def update(self, entity_id: ID, entity: Any) -> T:
        entity_dict = entity.model_dump(by_alias=True, exclude={"id"})
        entity_dict["updated_at"] = utcnow()

        current_document = await self.find_by_id(entity_id)

        """
        for idx, current_document in enumerate(self.memory):
            if getattr(current_document, "id", None) == entity_id:
                # Atualiza os campos do objeto existente
                for key, value in entity_dict.items():
                    setattr(current_document, key, value)
                self.memory[idx] = current_document
                return current_document
        raise NotFoundException()
        """

        if current_document:
            # TODO XXX Atualizar os dados
            return self.model_class(**current_document)
        return None

    async def delete_by_id(self, entity_id: ID) -> bool:
        current_document = await self.find_by_id(entity_id)
        if current_document:
            # XXX TODO Remover
            ...
