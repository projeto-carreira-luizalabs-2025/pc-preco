from enum import Enum
from typing import List, Optional, Tuple, Union

from fastapi import APIRouter

from app.api.v2.routers.price_router import router as price_router_v2
from app.api.v2.routers.alerta_router import router as alert_router

router_configurations: List[Tuple[APIRouter, str, Optional[List[Union[str, Enum]]]]] = [
    (price_router_v2, "/api/v2", ["Preços (v2)"]),
    (alert_router, "/api/v2", ["Alertas"]),
]
