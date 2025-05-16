from app.models import Price
from dependency_injector import containers, providers

from app.repositories import PriceRepository
from app.services import HealthCheckService, PriceService
from app.settings import AppSettings

memory_prices = [
    Price(seller_id="1", sku="A", preco_de=100, preco_por=90),
    Price(seller_id="2", sku="B", preco_de=200, preco_por=180),
]

price_dicts = [p.model_dump() for p in memory_prices]


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings = providers.Singleton(AppSettings)

    # Repositórios
    price_repository = providers.Singleton(PriceRepository, memory=price_dicts)

    # Serviços
    health_check_service = providers.Singleton(
        HealthCheckService, checkers=config.health_check_checkers, settings=settings
    )

    price_service = providers.Singleton(PriceService, repository=price_repository)
