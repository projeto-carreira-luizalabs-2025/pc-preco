from sqlalchemy import Column, DateTime, Integer, String, JSON

from app.common.datetime import utcnow
from app.integrations.database.sqlalchemy_client import Base


class IdEntityBase(Base):
    """
    Classe base para entidades que possuem um ID.
    Esta classe deve ser herdada por todas as entidades que possuem um ID.
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)


class AuditEntityBase(Base):
    """
    Classe base para entidades que possuem auditoria.
    Esta classe deve ser herdada por todas as entidades que precisam de auditoria.
    """

    __abstract__ = True

    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    created_by = Column(JSON, nullable=False)
    updated_by = Column(JSON, nullable=False)


class PersistableEntityBase(IdEntityBase, AuditEntityBase):
    """
    Classe base para entidades persistentes.
    Esta classe deve ser herdada por todas as entidades que precisam ser persistidas no banco de dados.
    """

    __abstract__ = True


class SellerIdSkuPersistableEntityBase(PersistableEntityBase):
    """
    Classe base para entidades que possuem seller_id e sku.
    Esta classe deve ser herdada por todas as entidades que precisam de seller_id e sku.
    """

    __abstract__ = True

    seller_id = Column(String, nullable=False, index=True)
    sku = Column(String, nullable=False, index=True)
