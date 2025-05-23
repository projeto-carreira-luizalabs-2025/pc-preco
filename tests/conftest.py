from typing import Generator

import pytest
from dependency_injector import containers, providers
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.api_application import create_app
from app.api.router import routes as api_routes
from app.models import Price
from app.repositories import PriceRepository
from app.services import HealthCheckService, PriceService
from app.settings import AppSettings, api_settings


@pytest.fixture
def test_prices() -> list[Price]:
    return [
        Price(seller_id="1", sku="A", preco_de=100, preco_por=90),
        Price(seller_id="2", sku="B", preco_de=200, preco_por=180),
    ]


class TestContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    settings = providers.Singleton(AppSettings)

    price_repository = providers.Factory(
        PriceRepository,
        memory=providers.List(
            providers.Object(Price(seller_id="1", sku="A", preco_de=100, preco_por=90)),
            providers.Object(Price(seller_id="2", sku="B", preco_de=200, preco_por=180)),
        ),
    )

    health_check_service = providers.Factory(
        HealthCheckService, checkers=config.health_check_checkers, settings=settings
    )

    price_service = providers.Factory(PriceService, repository=price_repository)


@pytest.fixture
def container() -> Generator[TestContainer, None, None]:
    container_instance = TestContainer()
    container_instance.config.from_pydantic(api_settings)
    yield container_instance


@pytest.fixture
def app(container: TestContainer) -> FastAPI:
    app_instance = create_app(api_settings, api_routes)

    app_instance.container = container  # type: ignore[attr-defined]

    container.wire(modules=["app.api.common.routers.health_check_routers", "app.api.v1.routers.price_router"])
    return app_instance


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app) as client_instance:
        yield client_instance


@pytest.fixture
def price_repository(container: TestContainer) -> PriceRepository:
    return container.price_repository()


@pytest.fixture
def price_service(container: TestContainer) -> PriceService:
    return container.price_service()


@pytest.fixture
def health_check_service(container: TestContainer) -> HealthCheckService:
    return container.health_check_service()
