from sqlalchemy import Column, String

from app.integrations.database.sqlalchemy_client import SQLAlchemyClient

from ..models import Alert
from .base.sqlalchemy_crud_repository import SQLAlchemyCrudRepository
from .base.sqlalchemy_entity_base import CreatedAtMixin, IdEntityBase, SellerIdMixin, SkuMixin, UpdatedAtMixin


class AlertBase(IdEntityBase, SellerIdMixin, SkuMixin, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "pc_alertas"

    mensagem = Column(String, nullable=False)
    status = Column(String, nullable=False)


class AlertRepository(SQLAlchemyCrudRepository[Alert, AlertBase]):
    def __init__(self, sql_client: SQLAlchemyClient):
        """
        Inicializa o repositório de alertas com o cliente SQLAlchemy.
        :param sql_client: Instância do cliente SQLAlchemy.
        """
        super().__init__(sql_client=sql_client, model_class=Alert, entity_base_class=AlertBase)


__all__ = ["AlertRepository"]
