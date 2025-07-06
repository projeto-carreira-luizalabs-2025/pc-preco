from pydantic import BaseModel, Field
from app.common.datetime import utcnow
from datetime import datetime

from app.models.base import SellerSkuEntity


class Alert(SellerSkuEntity):
    id: int
    mensagem: str
    status: str
    created_at: datetime | None = Field(default_factory=utcnow, description="Data e hora da criação")
    updated_at: datetime | None = Field(None, description="Data e hora da atualização")
