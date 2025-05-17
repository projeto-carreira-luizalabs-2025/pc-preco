from typing import Generator

import pytest
from dependency_injector import containers, providers
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.api_application import create_app
from app.api.router import routes as api_routes
from app.models import Preco
from app.repositories import PrecoRepository
from app.services import HealthCheckService, PrecoService
from app.settings import AppSettings, api_settings


@pytest.fixture
def test_precos() -> list[Preco]:
    return [
        Preco(seller_id="1", sku="A", preco_de=100, preco_por=90),
        Preco(seller_id="2", sku="B", preco_de=200, preco_por=180),
    ]


class TestContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    settings = providers.Singleton(AppSettings)

    preco_repository = providers.Factory(
        PrecoRepository,
        memory=providers.List(
            providers.Object(Preco(seller_id="1", sku="A", preco_de=100, preco_por=90)),
            providers.Object(Preco(seller_id="2", sku="B", preco_de=200, preco_por=180)),
        ),
    )

    health_check_service = providers.Factory(
        HealthCheckService, checkers=config.health_check_checkers, settings=settings
    )

    preco_service = providers.Factory(PrecoService, repository=preco_repository)


@pytest.fixture
def container() -> Generator[TestContainer, None, None]:
    container_instance = TestContainer()
    container_instance.config.from_pydantic(api_settings)
    yield container_instance


@pytest.fixture
def app(container: TestContainer) -> FastAPI:
    app_instance = create_app(api_settings, api_routes)
    app_instance.container = container  # type: ignore[attr-defined]
    container.wire(modules=["app.api.common.routers.health_check_routers", "app.api.v1.routers.preco_router"])
    return app_instance


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app) as client_instance:
        yield client_instance


@pytest.fixture
def preco_repository(container: TestContainer) -> PrecoRepository:
    return container.preco_repository()


@pytest.fixture
def preco_service(container: TestContainer) -> PrecoService:
    return container.preco_service()


@pytest.fixture
def health_check_service(container: TestContainer) -> HealthCheckService:
    return container.health_check_service()
