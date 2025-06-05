from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.integrations.database.sqlalchemy_client import SQLAlchemyClient

from app.models import PersistableEntity, QueryModel, Price

from .async_crud_repository import AsyncCrudRepository
from .sqlalchemy_entity_base import PersistableEntityBase

T = TypeVar("T", bound=PersistableEntity)  # Modelo Pydantic
B = TypeVar("B", bound=PersistableEntityBase)  # Entidade base do SQLAlchemy
Q = TypeVar("Q", bound=QueryModel)


class SQLAlchemyCrudRepository(AsyncCrudRepository[T], Generic[T, B]):
    """
    Implementação de AsyncCrudRepository com o SQLAlchemy.
    Ponto de atenção: Cada método possui uma transação única.

    """

    def __init__(self, sql_client: SQLAlchemyClient, model_class: T, entity_base_class: B):
        self.sql_client = sql_client
        self.model_class = model_class
        self.entity_base_class = entity_base_class
        self.pk_fields = self.sql_client.get_pk_fields(self.entity_base_class)

    def to_base(self, model: T) -> B:
        """
        Converte um modelo para a entidade base. (Pydantic -> SQLAlchemy)
        """
        model_dict = model.model_dump()
        base = self.entity_base_class()

        for field, value in model_dict.items():
            if hasattr(base, field):
                setattr(base, field, value)
        return base

    def to_model(self, base: B | None) -> T | None:
        """
        Converte uma entidade base para um modelo. (SQLAlchemy -> Pydantic)
        """

        base_dict = self.sql_client.to_dict(base)
        if base_dict is None:
            return None

        model = self.model_class.model_validate(base_dict)
        return model

    async def create(self, model: T) -> T:
        """
        Salva uma entidade no repositório.
        """
        base = self.to_base(model)  # Converte o modelo pydantic para a entidade base do SQLAlchemy

        async with self.sql_client.make_session() as session:
            async with session.begin():
                session.add(base)
        created_model = self.to_model(base)
        return created_model

    async def _find_base_by_seller_id_sku_on_session(self, seller_id: str, sku: str, session) -> B | None:
        """
        Busca uma entidade base pelo seller_id e sku.
        """
        preco = self.sql_client.init_select_preco(self.entity_base_class)
        preco = preco.where(self.entity_base_class.seller_id == seller_id).where(self.entity_base_class.sku == sku)
        scalar = await session.execute(preco)
        base = scalar.scalar_one_or_none()

        return base

    async def find_by_seller_id_and_sku(self, seller_id: str, sku: str) -> T | None:
        """
        Busca uma entidade pelo seller_id e sku.
        """
        async with self.sql_client.make_session() as session:
            base = await self._find_base_by_seller_id_sku_on_session(seller_id, sku, session)
        model = self.to_model(base)

        print(model)

        return model

    async def find(self, filters: Q, limit: int = 20, offset: int = 0, sort: dict | None = None) -> list[T]:
        """
        Busca uma lista de entidades com base nos filtros, limite, offset e ordenação.
        """

    async def patch_by_seller_id_and_sku(self, seller_id, sku, patch_entity):
        """
        Atualiza uma entidade pelo seller_id e sku.
        """
