from app.api.common.schemas import ResponseEntity, SchemaType


class PriceSchema(SchemaType):
    seller_id: str
    sku: str
    preco_de: int
    preco_por: int


class PriceResponse(PriceSchema, ResponseEntity):
    """Resposta adicionando"""


class PriceCreate(PriceSchema):
    """Schema para criação Precos"""


class PriceUpdate(SchemaType):
    """Permite apenas a atualização do "preco_de" e "preco_por" """

    preco_de: int
    preco_por: int
