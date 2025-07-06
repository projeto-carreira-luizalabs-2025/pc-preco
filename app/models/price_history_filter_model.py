from datetime import datetime
from typing import Optional
from app.models import QueryModel


class PriceHistoryFilter(QueryModel):
    """Modelo de filtro para consultas de histórico de preços"""
    seller_id: Optional[str] = None
    sku: Optional[str] = None
    de__lt: Optional[int] = None
    de__gt: Optional[int] = None
    por__lt: Optional[int] = None
    por__gt: Optional[int] = None
    registered_at__lt: Optional[datetime] = None
    registered_at__gt: Optional[datetime] = None
