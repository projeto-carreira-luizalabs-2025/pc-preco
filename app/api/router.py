from enum import Enum
from typing import List, Optional, Tuple, Union

from fastapi import APIRouter

from app.api.v2.routers.price_router import router as price_router_v2

router_configurations: List[Tuple[APIRouter, str, Optional[List[Union[str, Enum]]]]] = [
    (price_router_v2, "/api/v2", ["Preços (v2)"]),
]
