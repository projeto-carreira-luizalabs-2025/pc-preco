from dependency_injector import containers, providers

from app.repositories import PrecoRepository
from app.services import HealthCheckService, PrecoService
from app.settings import AppSettings


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings = providers.Singleton(AppSettings)

    # Repositórios
    preco_repository = providers.Singleton(PrecoRepository)

    # Serviços
    health_check_service = providers.Singleton(
        HealthCheckService, checkers=config.health_check_checkers, settings=settings
    )

    preco_service = providers.Singleton(PrecoService, repository=preco_repository)
