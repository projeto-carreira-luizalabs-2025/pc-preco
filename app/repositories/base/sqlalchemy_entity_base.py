from sqlalchemy import JSON, Column, DateTime, Integer, String

from app.common.datetime import utcnow
from app.integrations.database.sqlalchemy_client import Base


class IdMixin:
    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)


class CreatedByMixin:
    created_by = Column(JSON, nullable=False)


class UpdatedByMixin:
    updated_by = Column(JSON, nullable=False)


class CreatedAtMixin:
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class UpdatedAtMixin:
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class SellerIdMixin:
    seller_id = Column(String, nullable=False, index=True)


class SkuMixin:
    sku = Column(String, nullable=False, index=True)


class AuditEntityBase(Base, CreatedAtMixin, UpdatedAtMixin, CreatedByMixin, UpdatedByMixin):
    __abstract__ = True


class IdEntityBase(Base, IdMixin):
    __abstract__ = True


class PersistableEntityBase(IdEntityBase, AuditEntityBase):
    __abstract__ = True


class SellerIdSkuPersistableEntityBase(PersistableEntityBase, SellerIdMixin, SkuMixin):
    __abstract__ = True
