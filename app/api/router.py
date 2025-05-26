from app.api.v1 import router as price_router_v1
from app.api.v2 import router as price_router_v2

router_configurations = [
    (price_router_v1, "/api/v1", ["Preços (v1)"]),  # Use .router para acessar a instância do APIRouter
    (price_router_v2, "/api/v2", ["Preços (v2)"]),  # Use .router para acessar a instância do APIRouter
]
