from dependency_injector import containers, providers

from app.repositories import PriceRepository
from app.repositories.price_history_repository import PriceHistoryRepository
from app.services import HealthCheckService, PriceService
from app.services.price_history_service import PriceHistoryService
from app.settings import AppSettings

from app.integrations.database.sqlalchemy_client import SQLAlchemyClient

from app.integrations.auth.keycloak_adapter import KeycloakAdapter


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings = providers.Singleton(AppSettings)

    # Cliente SQLAlchemy
    sql_client = providers.Singleton(SQLAlchemyClient, config.app_db_url)

    # Keycloak

    keycloak_adapter = providers.Singleton(KeycloakAdapter, config.app_openid_wellknown)

    # Repositórios
    price_repository = providers.Singleton(PriceRepository, sql_client)
    price_history_repository = providers.Singleton(PriceHistoryRepository, sql_client)

    # Serviços
    health_check_service = providers.Singleton(
        HealthCheckService, checkers=config.health_check_checkers, settings=settings
    )

    price_history_service = providers.Singleton(PriceHistoryService,  repository=price_history_repository)
    
    price_service = providers.Singleton(PriceService, repository=price_repository)