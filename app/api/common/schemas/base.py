from datetime import datetime
from uuid import UUID as UuidType

from pydantic import BaseModel as SchemaType
from pydantic import ConfigDict, Field

from app.models.base import UserModel


class UuidSchema(SchemaType):
    id: UuidType | None = Field(None, description="Id único do objeto")


class IntSchema(SchemaType):
    id: int | None = Field(None, description="Identificador único do objeto")


class OwnershipSchema(SchemaType):
    """
    Em obras
    """

    ...


class AuditSchema(SchemaType):
    created_at: datetime | None = Field(None, description="Data e hora da criação")
    updated_at: datetime | None = Field(None, description="Data e hora da atualização")
    created_by: UserModel | None = Field(None, description="Criado por")
    updated_by: UserModel | None = Field(None, description="Atualizado por")


class ResponseEntity(AuditSchema, IntSchema, OwnershipSchema):

    model_config = ConfigDict(from_attributes=True)



class AuditHistorySchema(SchemaType):
    registered_at: datetime | None = Field(None, description="Data e hora de registro")
    created_at: datetime | None = Field(None, description="Data e hora da criação")
    updated_at: datetime | None = Field(None, description="Data e hora da atualização")


class ResponseHistoryEntity(AuditHistorySchema, IntSchema, OwnershipSchema):

    model_config = ConfigDict(from_attributes=True)