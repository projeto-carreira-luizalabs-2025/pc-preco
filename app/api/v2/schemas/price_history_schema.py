
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

from app.api.common.schemas import SchemaType
from app.api.common.schemas.base import ResponseEntityHistory
from app.api.common.schemas.response import ErrorResponse


class BasePriceHistoryModel(BaseModel):
    """Modelo base para histórico de precificação"""

    sku: str = Field(..., description="SKU do produto")
    seller_id: str = Field(..., description="ID do seller")
    de: int = Field(..., description="Preço anterior")
    por: int = Field(..., description="Preço atual")
    registered_at: datetime = Field(..., description="Data de registro do histórico")


class PriceHistoryResponse(BasePriceHistoryModel, ResponseEntityHistory):
    """Resposta do histórico de precificação"""

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "sku": "sku001",
                "seller_id": "abc123",
                "de": 1000,
                "por": 800,
                "registered_at": "2026-06-25T10:30:00Z"
            }
        }


class PriceHistoryCreate(SchemaType):
    """Schema para criação de histórico de precificação"""

    sku: str = Field(..., description="SKU do produto")
    seller_id: str = Field(..., description="ID do seller")
    de: int = Field(..., description="Preço anterior")
    por: int = Field(..., description="Preço atual")

    class Config:
        json_schema_extra = {
            "example": {
                "sku": "sku001",
                "seller_id": "abc123",
                "de": 1000,
                "por": 800
            }
        }


class PriceHistoryListResponse(BaseModel):
    """Lista de históricos de precificação"""

    __root__: List[PriceHistoryResponse]

    class Config:
        json_schema_extra = {
            "example": [
                {
                    "id": 1,
                    "sku": "sku001",
                    "seller_id": "abc123",
                    "de": 1000,
                    "por": 800,
                    "registered_at": "2026-06-25T10:30:00Z"
                },
                {
                    "id": 2,
                    "sku": "sku001",
                    "seller_id": "abc123",
                    "de": 800,
                    "por": 700,
                    "registered_at": "2026-05-16T09:12:00Z"
                }
            ]
        }


class PriceHistoryErrorResponse(ErrorResponse):
    """Schema para erros de histórico de preço"""

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
                        "ctx": {"value": -1},
                    }
                ],
            },
            "not_found": {
                "slug": "NOT_FOUND",
                "message": "Histórico não encontrado.",
                "details": [
                    {
                        "message": "Histórico de preço não encontrado.",
                        "location": "path",
                        "slug": "historico_nao_encontrado",
                        "field": "sku",
                        "ctx": {"seller_id": "abc123", "sku": "sku001"},
                    }
                ],
            },
        }
