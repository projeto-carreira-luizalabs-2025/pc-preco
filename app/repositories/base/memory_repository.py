from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel

from app.common.datetime import utcnow
from app.common.exceptions import NotFoundException

from .async_crud_repository import AsyncCrudRepository

T = TypeVar("T", bound=BaseModel)
ID = TypeVar("ID", bound=int | str)


class AsyncMemoryRepository(AsyncCrudRepository[T, ID], Generic[T, ID]):

    def __init__(self, memory=None):
        super().__init__()
        self.memory = memory if memory is not None else []

    async def create(self, entity: T) -> T:
        entity.created_at = utcnow()
        self.memory.append(entity)
        return entity

    async def find_by_id(self, entity_id: ID) -> Optional[T]:
        # XXX Aqui eu sei que something tem o id como o campo identity

        result = next((r for r in self.memory if r.identity == entity_id), None)
        if result:
            return result

        raise NotFoundException()

    async def find(self, filters: dict, limit: int = 10, offset: int = 0, sort: Optional[dict] = None) -> List[T]:

        filtered_list = [
            data
            for data in self.memory
            # TODO Criar filtro
        ]

        # XXX TODO Falta ordenar

        entities = []
        for document in filtered_list:
            entities.append(document)
        return entities

    async def update(self, entity_id: ID, entity: Any) -> T:
        entity_dict = entity.model_dump(by_alias=True, exclude={"id"})
        entity_dict["updated_at"] = utcnow()

        for idx, current_document in enumerate(self.memory):
            if getattr(current_document, "id", None) == entity_id:
                # Atualiza os campos do objeto existente
                for key, value in entity_dict.items():
                    setattr(current_document, key, value)
                self.memory[idx] = current_document
                return current_document
        raise NotFoundException()

    async def delete_by_id(self, entity_id: ID) -> None:
        # XXX TODO
        current_document = await self.find_by_id(entity_id)
        if not current_document:
            raise NotFoundException()
