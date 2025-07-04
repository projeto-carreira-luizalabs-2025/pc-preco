from dependency_injector import containers, providers

from app.repositories import PriceRepository
from app.services import HealthCheckService, PriceService
from app.settings import AppSettings

from app.integrations.database.sqlalchemy_client import SQLAlchemyClient

from app.integrations.auth.keycloak_adapter import KeycloakAdapter

from app.integrations.cache.redis_asyncio_adapter import RedisAsyncioAdapter


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings = providers.Singleton(AppSettings)

    # Cliente SQLAlchemy
    sql_client = providers.Singleton(SQLAlchemyClient, config.app_db_url)

    # Keycloak

    keycloak_adapter = providers.Singleton(KeycloakAdapter, config.app_openid_wellknown)

    # Redis

    redis_adapter = providers.Singleton(RedisAsyncioAdapter, config.app_redis_url)

    # Repositórios
    price_repository = providers.Singleton(PriceRepository, sql_client)

    # Serviços
    health_check_service = providers.Singleton(
        HealthCheckService, checkers=config.health_check_checkers, settings=settings
    )

    price_service = providers.Singleton(PriceService, repository=price_repository, redis_adapter=redis_adapter)
