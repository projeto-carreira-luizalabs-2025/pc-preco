from typing import Optional

from app.models import QueryModel


class AlertFilter(QueryModel):
    sku: Optional[str] = None
