from app.api.common.schemas import ResponseEntity, SchemaType
from app.api.common.schemas.response import ErrorResponse


class PriceSchema(SchemaType):
    seller_id: str
    sku: str
    preco_de: int
    preco_por: int

    class Config:
        schema_extra = {"example": {"seller_id": "abc123", "sku": "sku001", "preco_de": 29900, "preco_por": 19900}}


class PriceResponse(PriceSchema, ResponseEntity):
    """Resposta de uma precificação"""

    class Config:
        schema_extra = {
            "example": {
                "id": "uuid-da-resposta",
                "created_at": "2025-05-16T13:45:00Z",
                "updated_at": "2025-05-17T08:12:00Z",
                "seller_id": "abc123",
                "sku": "sku001",
                "preco_de": 29900,
                "preco_por": 19900,
            }
        }


class PriceCreate(PriceSchema):
    """Schema para criação de precificações"""

    class Config:
        schema_extra = {"example": {"seller_id": "abc123", "sku": "sku001", "preco_de": 29900, "preco_por": 19900}}


class PriceUpdate(SchemaType):
    """Permite apenas a atualização de 'preco_de' e 'preco_por'"""

    preco_de: int
    preco_por: int

    class Config:
        schema_extra = {"example": {"preco_de": 29900, "preco_por": 18900}}


class PriceErrorResponse(ErrorResponse):
    """Schema para erros de preços"""

    class Config:
        schema_extra = {
            "preco_de": {
                "slug": "BAD_REQUEST",
                "message": "Erro de validação",
                "details": [
                    {
                        "message": "preco_de deve ser maior que zero.",
                        "location": "body",
                        "slug": "preco_invalido",
                        "field": "preco_de",
                        "ctx": {"value": -10},
                    }
                ],
            },
            "not_found": {
                "slug": "NOT_FOUND",
                "message": "Not found",
                "details": [
                    {
                        "message": "Preço para produto não encontrado.",
                        "location": "path",
                        "slug": "preco_nao_encontrado",
                        "field": "sku",
                        "ctx": {"seller_id": "abc123", "sku": "sku001"},
                    }
                ],
            },
            "unprocessable_entity": {
                "slug": "UNPROCESSABLE_ENTITY",
                "message": "Unprocessable Entity",
                "details": [
                    {
                        "message": "Input should be less than or equal to 100",
                        "location": "query",
                        "slug": "less_than_equal",
                        "field": "_limit",
                        "ctx": {"le": 100},
                    }
                ],
            },
        }
