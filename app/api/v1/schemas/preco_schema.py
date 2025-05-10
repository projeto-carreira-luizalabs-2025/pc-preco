from app.api.common.schemas import ResponseEntity, SchemaType


class PrecoSchema(SchemaType):
    seller_id: str
    sku: str
    preco_de: int
    preco_por: int


class PrecoResponse(PrecoSchema, ResponseEntity):
    """Resposta adicionando"""


class PrecoCreate(PrecoSchema):
    """Schema para criação Precos"""


class PrecoUpdate(SchemaType):
    """Permite apenas a atualização do "preco_de" e "preco_por" """

    preco_de: int
    preco_por: int
