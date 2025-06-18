from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from app.api.common.schemas import Paginator
from app.common.exceptions import NotFoundException
from app.models.base import PersistableEntity
from app.repositories import AsyncCrudRepository
from app.models import QueryModel

T = TypeVar("T", bound=PersistableEntity)


class CrudService(ABC, Generic[T]):
    def __init__(self, repository: AsyncCrudRepository[T], context=None, author=None):
        self.repository = repository
        self._context = context
        self._author = author

    @property
    def context(self):
        return None

    @property
    def author(self):
        # XXX Pegar depois
        return None

    async def create(self, entity: Any) -> T:
        return await self.repository.create(entity)

    async def find(self, paginator: Paginator, filters: dict) -> list[T]:
        models_list = await self.repository.find(
            filters=filters, limit=paginator.limit, offset=paginator.offset, sort=paginator.get_sort_order()
        )
        return models_list

    async def find_by_seller_id_and_sku(self, seller_id: str, sku: str, can_raise_exception: bool = True) -> T | None:
        entity = await self.repository.find_by_seller_id_and_sku(seller_id, sku)
        return entity

    async def update_by_seller_id_and_sku(self, seller_id: str, sku: str, entity: T) -> T:
        return await self.repository.update_by_seller_id_and_sku(seller_id, sku, entity)

    async def patch_by_seller_id_and_sku(self, seller_id: str, sku: str, patch_data: dict) -> T:
        return await self.repository.patch_by_seller_id_and_sku(seller_id, sku, patch_data)

    async def delete_by_seller_id_and_sku(self, seller_id: str, sku: str):
        return await self.repository.delete_by_seller_id_and_sku(seller_id, sku)
