from datetime import datetime
from typing import ClassVar, Type, TypeVar
from uuid import UUID as UuidType

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from uuid_extensions import uuid7

from app.common.datetime import utcnow

T = TypeVar('T', bound='PersistableEntity')


class UuidModel(BaseModel):
    """
    Modelo base que fornece um campo de identificação UUID.
    """

    id: UuidType = Field(default_factory=uuid7, alias="_id")


class AuditModel(BaseModel):
    """
    Modelo base que fornece campos de auditoria para rastreamento de alterações.
    """

    created_at: datetime | None = Field(default_factory=utcnow, description="Data e hora da criação")
    updated_at: datetime | None = Field(None, description="Data e hora da atualização")
    created_by: str | None = Field(None, description="Criado por")
    updated_by: str | None = Field(None, description="Atualizado por")

    audit_created_at: datetime | None = Field(None, description="Data e hora da efetiva criação do registro")
    audit_updated_at: datetime | None = Field(None, description="Data e hora da efetiva atualização do registro")


class PersistableEntity(UuidModel, AuditModel):
    """
    Entidade base para todos os modelos persistíveis no sistema.
    Combina identificação UUID e campos de auditoria.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_json(cls: Type[T], json_data: str) -> T:
        """
        Converte uma string JSON em uma instância da classe.

        :param json_data: String JSON contendo os dados do objeto
        :return: Instância da classe criada a partir do JSON
        """
        return TypeAdapter(cls).validate_json(json_data)
