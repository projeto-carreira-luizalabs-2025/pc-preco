from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel

from app.common.datetime import utcnow

from .async_crud_repository import AsyncCrudRepository

T = TypeVar("T", bound=BaseModel)
ID = TypeVar("ID", bound=int | str)


class AsyncMemoryRepository(AsyncCrudRepository[T], Generic[T, ID]):

    def __init__(self, key_name: str, model_class: Type[T]):
        super().__init__()
        self.key_name = key_name
        self.memory: list[dict] = []
        self.model_class = model_class

    async def create(self, entity: T) -> T:
        entity_dict = entity.model_dump(by_alias=True)
        entity_dict["created_at"] = utcnow()

        self.memory.append(entity_dict)

        return entity

    async def find_by_id(self, entity_id: ID) -> Optional[T]:
        result = next((r for r in self.memory if r[self.key_name] == entity_id), None)
        if result is not None:
            return self.model_class(**result)
        return None

    @staticmethod
    def _can_filter(data: Dict[str, Any], filters: Dict[str, Any] | None) -> bool:
        filters = filters or {}

        for key, value in filters.items():
            if value is not None and data.get(key) != value:
                return False
        return True

    async def find(
        self, filters: Dict[str, Any], limit: int = 10, offset: int = 0, sort: Optional[Dict[str, int]] = None
    ) -> List[T]:
        filtered_list = [data for data in self.memory if self._can_filter(data, filters)]

        # Ordenação
        if sort:
            # Tirar os espaços de chaves do sort
            stripped_sort = {key.strip(): value for key, value in sort.items()}

            for field, direction in reversed(list(stripped_sort.items())):
                reverse = direction == -1
                filtered_list = [item for item in filtered_list if item.get(field) is not None]
                # Usando uma função de ordenação typesafe
                filtered_list = sorted(
                    filtered_list, key=lambda x, current_field=field: x.get(current_field, 0), reverse=reverse
                )

        # Paginação
        paginated_list = filtered_list[offset : offset + limit]

        entities = [self.model_class(**document) for document in paginated_list]
        return entities

    async def update(self, entity_id: ID, entity: Any) -> T:
        entity_dict = entity.model_dump(by_alias=True, exclude={"id"})
        entity_dict["updated_at"] = utcnow()

        for idx, current_document in enumerate(self.memory):
            if current_document.get(self.key_name) == entity_id:
                # Atualiza o dicionário com os novos valores
                updated = {**current_document, **entity_dict}
                self.memory[idx] = updated
                return self.model_class(**updated)

        # Se não encontrou o documento, retorna None (ou poderia lançar uma exceção)
        raise ValueError(f"Entity with id {entity_id} not found")

    async def delete_by_id(self, entity_id: ID) -> None:
        current_document = await self.find_by_id(entity_id)

        if not current_document:
            return None

        self.memory = [doc for doc in self.memory if doc.get(self.key_name) != entity_id]
