from typing import Optional

from app.models.query import QueryModel


class PriceFilter(QueryModel):
    de__lt: Optional[int] = None
    de__gt: Optional[int] = None
    por__lt: Optional[int] = None
    por__gt: Optional[int] = None
    sku: Optional[str] = None
