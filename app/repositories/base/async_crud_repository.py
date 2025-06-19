from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")
Q = TypeVar("Q")


class AsyncCrudRepository(ABC, Generic[T]):
    """
    Interface genérica para operações de repositório CRUD.
    """

    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        Salva uma entidade no repositório.
        """

    @abstractmethod
    async def find_by_seller_id_and_sku(self, seller_id: str, sku: str) -> T | None:
        """
        Busca uma entidade pelo seller_id e sku.
        """

    @abstractmethod
    async def find(self, filters: Q, limit: int = 20, offset: int = 0, sort: dict | None = None) -> list[T]:
        """
        Busca entidades no repositório, utilizando filtros e paginação.
        """

    @abstractmethod
    async def update_by_seller_id_and_sku(self, seller_id: str, sku: str, entity: T) -> T:
        """
        Atualiza uma entidade existente no repositório.
        """

    @abstractmethod
    async def patch_by_seller_id_and_sku(self, seller_id: str, sku: str, patch_entity: dict) -> T:
        """
        Atualiza uma entidade somente com os campos informados no dicionário.
        """

    @abstractmethod
    async def delete_by_seller_id_and_sku(self, seller_id: str, sku: str) -> bool:
        """
        Remove uma entidade pelo seu identificador único.
        """
