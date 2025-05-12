from pydantic import PositiveInt

from app.api.common.schemas import ResponseEntity, SchemaType


class SomethingBase(SchemaType):
    identify: PositiveInt


class SomethingSchema(SomethingBase):
    name: str
    value: int


class SomethingResponse(SomethingSchema, ResponseEntity):
    """Resposta adicionando"""


class SomethingCreate(SomethingSchema):
    """Schema para criação Somethings"""


class SomethingCreateResponse(SomethingBase):
    """
    Resposta para a criação de alguma coisa
    """


class SomethingUpdate(SchemaType):
    """Permite apenas a atualização do nome e do valor"""

    name: str
    value: int
