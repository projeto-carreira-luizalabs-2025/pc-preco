from pydantic import BaseModel, Field

from app.api.common.schemas.base import CreatedAtMixin, IntSchema, UpdatedAtMixin

from .base_schema import SellerSkuBaseModel


class BaseAlertModel(BaseModel):
    """Modelo base para alertas"""

    mensagem: str = Field(..., description="Mensagem do alerta")
    status: str = Field(..., description="Status do alerta, ex: pendente, resolvido, etc.")


class AlertCreate(SellerSkuBaseModel, BaseAlertModel):
    """Schema para criação de alertas"""


class AlertResponse(BaseAlertModel, IntSchema, CreatedAtMixin, UpdatedAtMixin):
    """Resposta de uma precificação"""

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "created_at": "2025-05-16T13:45:00Z",
                "updated_at": "2025-05-17T08:12:00Z",
                "seller_id": "abc123",
                "sku": "sku001",
                "mensagem": "Alerta de preço pendente",
                "status": "pendente",
            }
        }
