from app.models import Preco
from dependency_injector import containers, providers

from app.repositories import PrecoRepository
from app.services import HealthCheckService, PrecoService
from app.settings import AppSettings

memory_precos = [
    Preco(seller_id="1", sku="A", preco_de=100, preco_por=90),
    Preco(seller_id="2", sku="B", preco_de=200, preco_por=180),
]

preco_dicts = [p.model_dump() for p in memory_precos]


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings = providers.Singleton(AppSettings)

    # Repositórios
    preco_repository = providers.Singleton(PrecoRepository, memory=preco_dicts)

    # Serviços
    health_check_service = providers.Singleton(
        HealthCheckService, checkers=config.health_check_checkers, settings=settings
    )

    preco_service = providers.Singleton(PrecoService, repository=preco_repository)
