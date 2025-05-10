from app.api.common.schemas import ResponseEntity, SchemaType


class PrecoSchema(SchemaType):
    identity: int
    name: str
    value: int


class PrecoResponse(PrecoSchema, ResponseEntity):
    """Resposta adicionando"""


class PrecoCreate(PrecoSchema):
    """Schema para criação Precos"""


class PrecoUpdate(SchemaType):
    """Permite apenas a atualização do nome e do valor"""

    name: str
    value: int
