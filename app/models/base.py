from datetime import datetime
from uuid import UUID as UuidType

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from uuid_extensions import uuid7

from app.common.datetime import utcnow

# --- Mixins ---


class IdModel(BaseModel):
    id: UuidType | int | None = Field(None, description="Chave")


class IntModel(BaseModel):
    id: int | None = Field(None, description="Identificador")


class UuidModel(BaseModel):
    id: UuidType = Field(default_factory=uuid7, alias="_id")


class SellerIdMixin(BaseModel):
    seller_id: str = Field(..., description="ID do seller")


class SkuMixin(BaseModel):
    sku: str = Field(..., description="ID do produto")


class UserModel(BaseModel):
    name: str | None  # sub
    server: str | None  # iss


class CreatedAtMixin(BaseModel):
    created_at: datetime | None = Field(default_factory=utcnow, description="Data e hora da criação")


class UpdatedAtMixin(BaseModel):
    updated_at: datetime | None = Field(None, description="Data e hora da atualização")


class CreatedByMixin(BaseModel):
    created_by: UserModel | None = Field(None, description="Criado por")


class UpdatedByMixin(BaseModel):
    updated_by: UserModel | None = Field(None, description="Atualizado por")


class SellerSkuEntity(SellerIdMixin, SkuMixin):
    def get_sellerid_sku(self) -> dict:
        return {"seller_id": self.seller_id, "sku": self.sku}


class AuditModel(CreatedAtMixin, UpdatedAtMixin, CreatedByMixin, UpdatedByMixin):
    pass


class PersistableEntity(AuditModel, IdModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_json(cls, json_data: str):
        return TypeAdapter(cls).validate_json(json_data)


class UuidPersistableEntity(UuidModel, AuditModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_json(cls, json_data: str):
        return TypeAdapter(cls).validate_json(json_data)


class IntPersistableEntity(IntModel, AuditModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_json(cls, json_data: str):
        return TypeAdapter(cls).validate_json(json_data)


class SellerSkuUuidPersistableEntity(UuidPersistableEntity, SellerSkuEntity):
    """
    Entidade com seller_id e sku e chave uuid.
    """


class SellerSkuIntPersistableEntity(IntPersistableEntity, SellerSkuEntity):
    """
    Entidade com seller_id e sku e chave int.
    """
