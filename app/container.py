from dependency_injector import containers, providers

from app.repositories import PriceRepository
from app.services import HealthCheckService, PriceService
from app.settings import AppSettings

from app.integrations.database.sqlalchemy_client import SQLAlchemyClient


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings = providers.Singleton(AppSettings)

    # Cliente SQLAlchemy
    sql_client = providers.Singleton(SQLAlchemyClient, config.app_db_url)

    # Repositórios
    price_repository = providers.Singleton(PriceRepository, sql_client)

    # Serviços
    health_check_service = providers.Singleton(
        HealthCheckService, checkers=config.health_check_checkers, settings=settings
    )

    price_service = providers.Singleton(PriceService, repository=price_repository)
