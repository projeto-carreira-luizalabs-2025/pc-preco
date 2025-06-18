from typing import Generator

import pytest
from dependency_injector import providers
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.api_application import create_app
from app.api.router import router_configurations as api_routes
from app.container import Container
from app.models import Price
from app.repositories import PriceRepository
from app.services import HealthCheckService, PriceService
from app.settings import api_settings

from tests.factories.price_repository_mock_factory import PriceRepositoryMockFactory


@pytest.fixture
def test_prices() -> list[Price]:
    return [
        Price(
            seller_id="1",
            sku="A",
            de=100,
            por=90,
            updated_at=None,
            created_by=None,
            updated_by=None,
            audit_created_at=None,
            audit_updated_at=None,
        ),
        Price(
            seller_id="2",
            sku="B",
            de=200,
            por=180,
            updated_at=None,
            created_by=None,
            updated_by=None,
            audit_created_at=None,
            audit_updated_at=None,
        ),
    ]


@pytest.fixture
def mock_price_repository() -> PriceRepository:
    """
    Cria um repositório mockado usando a factory centralizada.
    """
    return PriceRepositoryMockFactory.create_mock_repository()


@pytest.fixture
def container(mock_price_repository: PriceRepository) -> Generator[Container, None, None]:
    container = Container()
    container.config.from_pydantic(api_settings)

    # Sobrescreve o repositório para usar dados de teste
    container.price_repository.override(providers.Object(mock_price_repository))

    yield container
    container.unwire()


@pytest.fixture
def app(container: Container) -> Generator[FastAPI, None, None]:
    import app.api.common.routers.health_check_routers as health_check_routers
    import app.api.v2.routers.price_router as price_router_v2

    container.wire(
        modules=[
            health_check_routers,
            price_router_v2,
        ]
    )

    app_instance = create_app(api_settings, api_routes)
    app_instance.container = container  # type: ignore[attr-defined]

    yield app_instance
    container.unwire()


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app) as client_instance:
        yield client_instance


@pytest.fixture
def price_repository(container: Container) -> PriceRepository:
    return container.price_repository()


@pytest.fixture
def price_service(container: Container) -> PriceService:
    return container.price_service()


@pytest.fixture
def health_check_service(container: Container) -> HealthCheckService:
    return container.health_check_service()
