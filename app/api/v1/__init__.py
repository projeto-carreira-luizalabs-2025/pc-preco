from fastapi import APIRouter

from app.settings import api_settings

SELLER_V1_PREFIX = "/seller/v1"

router_selller = APIRouter(prefix=SELLER_V1_PREFIX)


def load_routes(router_seller: APIRouter):
    if api_settings.enable_seller_resources:
        from app.api.v1.routers.preco_router import router as preco_router

        router_seller.include_router(preco_router)


load_routes(router_selller)
