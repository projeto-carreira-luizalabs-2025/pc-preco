from fastapi import APIRouter

router = APIRouter(tags=["Preços (v2)"])


def load_routes(api_router: APIRouter):
    from app.settings import api_settings

    if api_settings.enable_seller_resources:
        from app.api.v2.routers.price_router import router as price_router_v2_instance

        api_router.include_router(price_router_v2_instance)


load_routes(router)
