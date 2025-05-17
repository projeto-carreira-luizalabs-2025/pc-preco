from typing import Any, Generic, List, Optional, TypeVar
from uuid import UUID as PythonUUID

from app.common.datetime import utcnow
from app.common.exceptions import NotFoundException
from app.models.base import PersistableEntity

from .async_crud_repository import AsyncCrudRepository

T = TypeVar("T", bound=PersistableEntity)
ID = TypeVar("ID", bound=int | str | PythonUUID)


class AsyncMemoryRepository(AsyncCrudRepository[T, ID], Generic[T, ID]):

    def __init__(self, memory: Optional[List[T]] = None):
        super().__init__()
        self.memory: List[T] = memory if memory is not None else []

    async def create(self, entity: T) -> T:
        entity.created_at = utcnow()
        self.memory.append(entity)
        return entity

    async def find_by_id(self, entity_id: ID) -> Optional[T]:
        result = next((r for r in self.memory if r.id == entity_id), None)
        if result:
            return result

        raise NotFoundException()

    async def find(self, filters: dict, limit: int = 10, offset: int = 0, sort: Optional[dict] = None) -> List[T]:

        filtered_list = [
            data
            for data in self.memory
            # TODO Criar filtro
        ]

        if sort:
            stripped_sort = {key.strip(): value for key, value in sort.items()}

            for field, direction in reversed(list(stripped_sort.items())):
                reverse = direction == -1

                def sort_key(item: T) -> Any:
                    value = getattr(item, field, None)
                    return (value is None, value)

                filtered_list = sorted(filtered_list, key=sort_key, reverse=reverse)

        paginated_list = filtered_list[offset : offset + limit]

        entities: List[T] = []
        for document in paginated_list:
            entities.append(document)
        return entities

    async def update(self, entity_id: ID, entity: Any) -> T:
        update_data_dict = entity.model_dump(exclude_unset=True, by_alias=True, exclude={"id"})
        update_data_dict["updated_at"] = utcnow()

        for idx, current_document in enumerate(self.memory):
            if current_document.id == entity_id:
                for key, value in update_data_dict.items():
                    setattr(current_document, key, value)
                return current_document
        raise NotFoundException()

    async def delete_by_id(self, entity_id: ID) -> None:
        await self.find_by_id(entity_id)
        self.memory = [doc for doc in self.memory if doc.id != entity_id]
