import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.common.datetime import utcnow
from app.integrations.database.sqlalchemy_client import SQLAlchemyClient
from app.models import PersistableEntity, Price, QueryModel

from .async_crud_repository import AsyncCrudRepository
from .sqlalchemy_entity_base import PersistableEntityBase

T = TypeVar("T", bound=PersistableEntity)  # Modelo Pydantic
B = TypeVar("B", bound=PersistableEntityBase)  # Entidade base do SQLAlchemy
Q = TypeVar("Q", bound=QueryModel)

CAMPOS_IMUTAVEIS = {"created_by", "created_at"}

logger = logging.getLogger(__name__)


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
        logger.info("Criando entidade", extra={"dados": model.model_dump()})
        base = self.to_base(model)  # Converte o modelo pydantic para a entidade base do SQLAlchemy

        async with self.sql_client.make_session() as session:
            async with session.begin():
                session.add(base)
        logger.debug("Entidade criada no banco", extra={"dados": str(base)})
        created_model = self.to_model(base)
        return created_model

    async def _find_base_by_seller_id_sku_on_session(self, seller_id: str, sku: str, session) -> B | None:
        """
        Busca uma entidade base pelo seller_id e sku.
        """
        preco = self.sql_client.init_select(self.entity_base_class)
        preco = preco.where(self.entity_base_class.seller_id == seller_id).where(self.entity_base_class.sku == sku)
        scalar = await session.execute(preco)
        base = scalar.scalar_one_or_none()
        return base

    async def find_by_seller_id_and_sku(self, seller_id: str, sku: str) -> T | None:
        """
        Busca uma entidade pelo seller_id e sku.
        """
        logger.info(
            "Buscando entidade por seller_id=%s, sku=%s", seller_id, sku, extra={"seller_id": seller_id, "sku": sku}
        )
        async with self.sql_client.make_session() as session:
            base = await self._find_base_by_seller_id_sku_on_session(seller_id, sku, session)
        model = self.to_model(base)
        if model:
            logger.debug("Entidade encontrada", extra={"dados": model.model_dump()})
        else:
            logger.warning("Nenhuma entidade encontrada para seller_id=%s, sku=%s", seller_id, sku)
        return model

    def _apply_sort(self, stmt, sort: dict):
        for field, direction in sort.items():
            if hasattr(self.entity_base_class, field):
                column = getattr(self.entity_base_class, field)
                stmt = stmt.order_by(column.desc() if direction == -1 else column.asc())
        return stmt

    async def find(self, filters: Q, limit: int = 20, offset: int = 0, sort: dict | None = None) -> list[T]:
        """
        Busca uma lista de entidades com base nos filtros, limite, offset e ordenação.
        """
        logger.info(
            "Buscando entidades",
            extra={"filtros": filters.to_query_dict(), "limit": limit, "offset": offset, "sort": sort},
        )

        def apply_operator(stmt, column, op, v):
            if op == "$lt":
                return stmt.where(column < v)
            elif op == "$lte":
                return stmt.where(column <= v)
            elif op == "$gt":
                return stmt.where(column > v)
            elif op == "$gte":
                return stmt.where(column >= v)
            return stmt

        async with self.sql_client.make_session() as session:
            stmt = self.sql_client.init_select(self.entity_base_class)

            for field, value in filters.to_query_dict().items():
                if not hasattr(self.entity_base_class, field):
                    logger.debug(f"Campo '{field}' não existe em {self.entity_base_class.__name__}, ignorando filtro.")
                    continue
                column = getattr(self.entity_base_class, field)
                if isinstance(value, dict):
                    for op, v in value.items():
                        stmt = apply_operator(stmt, column, op, v)
                else:
                    stmt = stmt.where(column == value)

            if sort:
                stmt = self._apply_sort(stmt, sort)

            stmt = stmt.limit(limit).offset(offset)
            result = await session.execute(stmt)
            bases = result.scalars().all()
            logger.info(
                "Encontradas %d entidades para os filtros informados.", len(bases), extra={"quantidade": len(bases)}
            )
            return [self.to_model(base) for base in bases]

    async def delete_by_seller_id_and_sku(self, seller_id: str, sku: str) -> bool:
        """
        Deleta uma entidade pelo seller_id e sku.
        """
        logger.info(
            "Deletando entidade por seller_id=%s, sku=%s", seller_id, sku, extra={"seller_id": seller_id, "sku": sku}
        )
        async with self.sql_client.make_session() as session:
            async with session.begin():
                stmt = self.sql_client.init_delete(self.entity_base_class)
                stmt = stmt.where(self.entity_base_class.seller_id == seller_id).where(
                    self.entity_base_class.sku == sku
                )
                result = await session.execute(stmt)
            deleted = result.rowcount > 0
            if deleted:
                logger.info(
                    "Entidade deletada para seller_id=%s, sku=%s",
                    seller_id,
                    sku,
                    extra={"seller_id": seller_id, "sku": sku},
                )
            else:
                logger.warning(
                    "Nenhuma entidade deletada para seller_id=%s, sku=%s",
                    seller_id,
                    sku,
                    extra={"seller_id": seller_id, "sku": sku},
                )
            return deleted

    async def update_by_seller_id_and_sku(self, seller_id: str, sku: str, model: T) -> T | None:
        """
        Atualiza uma entidade pelo seller_id e sku.
        Se a entidade não existir, retorna None.
        """
        logger.info(
            "Atualizando entidade por seller_id=%s, sku=%s", seller_id, sku, extra={"dados": model.model_dump()}
        )
        async with self.sql_client.make_session() as session:
            async with session.begin():
                base = await self._find_base_by_seller_id_sku_on_session(seller_id, sku, session)
                if can_update := base is not None:
                    base.updated_at = utcnow()
                    for key, value in model.model_dump().items():
                        if key not in CAMPOS_IMUTAVEIS and key not in self.pk_fields:
                            setattr(base, key, value)
                    base.updated_at = utcnow()
            if can_update:
                await session.commit()
                logger.info(
                    "Entidade atualizada para seller_id=%s, sku=%s",
                    seller_id,
                    sku,
                    extra={"seller_id": seller_id, "sku": sku},
                )
            else:
                logger.warning(
                    "Nenhuma entidade encontrada para atualizar seller_id=%s, sku=%s",
                    seller_id,
                    sku,
                    extra={"seller_id": seller_id, "sku": sku},
                )
        model = self.to_model(base)
        return model
