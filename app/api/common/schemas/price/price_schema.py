from app.api.common.schemas import ResponseEntity, SchemaType
from app.api.common.schemas.response import ErrorResponse


class PriceSchema(SchemaType):
    seller_id: str
    sku: str
    de: int
    por: int

    class Config:
        json_schema_extra = {"example": {"seller_id": "abc123", "sku": "sku001", "de": 1000, "por": 500}}


class PriceResponse(PriceSchema, ResponseEntity):
    """Resposta de uma precificação"""

    class Config:
        json_schema_extra = {
            "example": {
                "id": "uuid-da-resposta",
                "created_at": "2025-05-16T13:45:00Z",
                "updated_at": "2025-05-17T08:12:00Z",
                "created_by": "user_id",
                "updated_by": "user_id",
                "seller_id": "abc123",
                "sku": "sku001",
                "de": 1000,
                "por": 500,
            }
        }


class PriceCreate(PriceSchema):
    """Schema para criação de precificações"""

    class Config:
        json_schema_extra = {"example": {"seller_id": "abc123", "sku": "sku001", "de": 1000, "por": 500}}


class PriceUpdate(SchemaType):
    """Permite apenas a atualização dos atributos 'de' e 'por'"""

    de: int
    por: int

    class Config:
        json_schema_extra = {"example": {"de": 1000, "por": 500}}


class PricePatch(SchemaType):
    """Permite atualização parcial dos atributos 'de' e 'por'"""

    de: int | None = None
    por: int | None = None

    class Config:
        json_schema_extra = {"example": {"de": 1000}}


class PriceErrorResponse(ErrorResponse):
    """Schema para erros de preços"""

    class Config:
        json_schema_extra = {
            "de": {
                "slug": "BAD_REQUEST",
                "message": "Erro de validação",
                "details": [
                    {
                        "message": "O campo 'de' deve ser maior que zero.",
                        "location": "body",
                        "slug": "preco_invalido",
                        "field": "de",
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
