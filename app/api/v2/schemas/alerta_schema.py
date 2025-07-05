from pydantic import BaseModel, Field

from .base_schema import SellerSkuBaseModel


class BaseAlertModel(BaseModel):
    """Modelo base para alertas"""

    mensagem: str = Field(..., description="Mensagem do alerta")
    status: str = Field(..., description="Status do alerta, ex: pendente, resolvido, etc.")


class AlertCreate(SellerSkuBaseModel, BaseAlertModel):
    """Schema para criação de alertas"""
