from fastapi import APIRouter

router = APIRouter(tags=["Preços (v1)"])


def load_routes(api_router: APIRouter):
    from app.settings import api_settings

    if api_settings.enable_seller_resources:
        from app.api.v1.routers.price_router import router as price_router_v1_instance

        api_router.include_router(price_router_v1_instance)


load_routes(router)
