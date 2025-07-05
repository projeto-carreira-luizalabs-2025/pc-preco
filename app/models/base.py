from datetime import datetime
from uuid import UUID as UuidType

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from uuid_extensions import uuid7

from app.common.datetime import utcnow


class IdModel(BaseModel):
    id: UuidType | int | None = Field(None, description="Chave")


class IntModel(BaseModel):
    id: int | None = Field(None, description="Identificador")


class UuidModel(BaseModel):
    id: UuidType = Field(default_factory=uuid7, alias="_id")


class UserModel(BaseModel):
    """
    Na _facilidade_ do JWT do Keyclok, vamos utilizar o `sub` como o `name` e
    o `iss` como o `server`. Aí, para identificar o usuário, a pessoa que está
    auditando irá consultar estes dados no Keycloak.
    """

    name: str | None  # sub
    server: str | None  # iss


class AuditModel(BaseModel):
    created_at: datetime | None = Field(default_factory=utcnow, description="Data e hora da criação")
    updated_at: datetime | None = Field(None, description="Data e hora da atualização")
    created_by: UserModel | None = Field(None, description="Criado por")
    updated_by: UserModel | None = Field(None, description="Atualizado por")


class PersistableEntity(AuditModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_json(cls, json_data: str):
        return TypeAdapter(cls).validate_json(json_data)


class UuidPersistableEntity(UuidModel, PersistableEntity):
    """
    Entidade cuja chave é um uuid
    """


class IntPersistableEntity(IntModel, PersistableEntity):
    """
    Entidiade cuja chave é um inteiro.
    """


class SellerSkuEntity(BaseModel):
    seller_id: str = Field(..., description="ID do seller")
    sku: str = Field(..., description="ID do produto")

    def get_sellerid_sku(self) -> dict:
        return {"seller_id": self.seller_id, "sku": self.sku}


class SellerSkuUuidPersistableEntity(UuidPersistableEntity, SellerSkuEntity):
    """
    Entidade com seller_id e sku e chave uuid.
    """


class SellerSkuIntPersistableEntity(IntPersistableEntity, SellerSkuEntity):
    """
    Entidade com seller_id e sku e chave int.
    """


class AuditHistoryModel(BaseModel):
    registered_at: datetime | None = Field(default_factory=utcnow, description="Data e hora da criação")
    created_at: datetime | None = Field(default_factory=utcnow, description="Data e hora da criação")
    updated_at: datetime | None = Field(None, description="Data e hora da atualização")

class PersistableHistoryEntity(AuditHistoryModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_json(cls, json_data: str):
        return TypeAdapter(cls).validate_json(json_data)

class IntPersistableHistoryEntity(IntModel, PersistableHistoryEntity):
    """
    Entidiade cuja chave é um inteiro.
    """
class SellerSkuIntHistoryPersistableEntity(IntPersistableHistoryEntity, SellerSkuEntity):
    """
    Entidade com seller_id e sku e chave int.
    """
