from pytest import fixture
from typing import Generator
from fastapi import FastAPI

from app.container import Container
from app.models import Price
from app.repositories import PriceRepository
from app.services import HealthCheckService, PriceService
from app.settings import api_settings
from app.api.api_application import create_app
from app.api.router import router_configurations as api_routes
from dependency_injector import providers
from tests.factories.price_repository_mock_factory import PriceRepositoryMockFactory


@fixture
def container(mock_price_repository: PriceRepository) -> Generator[Container, None, None]:
    container = Container()

    try:
        container.config.from_pydantic(api_settings)

        # Sobrescreve o repositório para usar dados de teste
        container.price_repository.override(providers.Object(mock_price_repository))

        yield container
    finally:
        container.unwire()


@fixture
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


@fixture
def price_repository(container: Container) -> PriceRepository:
    return container.price_repository()


@fixture
def price_service(container: Container) -> PriceService:
    return container.price_service()


@fixture
def health_check_service(container: Container) -> HealthCheckService:
    return container.health_check_service()


@fixture
def mock_price_repository() -> PriceRepository:
    """
    Cria um repositório mockado usando a factory centralizada.
    """
    return PriceRepositoryMockFactory.create_mock_repository()


@fixture
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
