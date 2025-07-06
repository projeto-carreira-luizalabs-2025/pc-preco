from datetime import datetime
from uuid import UUID as UuidType

from pydantic import BaseModel as SchemaType
from pydantic import ConfigDict, Field

from app.models.base import UserModel


class UuidSchema(SchemaType):
    id: UuidType | None = Field(None, description="Id único do objeto")


class IntSchema(SchemaType):
    id: int | None = Field(None, description="Identificador único do objeto")


class CreatedAtMixin(SchemaType):
    created_at: datetime | None = Field(None, description="Data e hora da criação")


class UpdatedAtMixin(SchemaType):
    updated_at: datetime | None = Field(None, description="Data e hora da atualização")


class CreatedByMixin(SchemaType):
    created_by: UserModel | None = Field(None, description="Criado por")


class UpdatedByMixin(SchemaType):
    updated_by: UserModel | None = Field(None, description="Atualizado por")


class AuditSchema(CreatedAtMixin, UpdatedAtMixin, CreatedByMixin, UpdatedByMixin):
    pass


class ResponseEntity(AuditSchema, IntSchema):

    model_config = ConfigDict(from_attributes=True)
