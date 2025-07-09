import os

import dotenv
from fastapi import FastAPI

from app.common.logging_config import setup_logging
from app.container import Container
from app.settings import api_settings

setup_logging()

ENV = os.getenv("ENV", "production")
is_dev = ENV == "dev"

dotenv.load_dotenv(override=is_dev)


def init() -> FastAPI:
    from app.api.api_application import create_app
    from app.api.router import router_configurations

    container = Container()

    container.config.from_dict(api_settings.model_dump())  # type: ignore[attr-defined]

    app_api = create_app(api_settings, router_configurations)
    app_api.container = container  # type: ignore[attr-defined]

    # Autowiring
    container.wire(modules=["app.api.common.routers.health_check_routers"])
    container.wire(modules=["app.api.v2.routers.price_router"])
    container.wire(modules=["app.api.v2.routers.alerta_router"])

    return app_api


app = init()
