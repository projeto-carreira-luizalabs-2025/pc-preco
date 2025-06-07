from typing import Optional
from app.models import QueryModel


class PriceFilter(QueryModel):
    de__lt: Optional[float] = None
    de__gt: Optional[float] = None
    por__lt: Optional[float] = None
    por__gt: Optional[float] = None
    sku: Optional[str] = None
