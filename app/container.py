from dependency_injector import containers, providers

from app.integrations.auth.keycloak_adapter import KeycloakAdapter
from app.integrations.cache.redis_asyncio_adapter import RedisAsyncioAdapter
from app.integrations.database.sqlalchemy_client import SQLAlchemyClient
from app.integrations.queue.rabbitmq_adapter import RabbitMQProducer
from app.repositories import AlertRepository, PriceRepository
from app.repositories.price_history_repository import PriceHistoryRepository
from app.services import AlertService, HealthCheckService, PriceService
from app.services.price_history_service import PriceHistoryService
from app.settings import AppSettings


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings = providers.Singleton(AppSettings)

    # Cliente SQLAlchemy
    sql_client = providers.Singleton(SQLAlchemyClient, config.app_db_url)

    # Keycloak
    keycloak_adapter = providers.Singleton(KeycloakAdapter, config.app_openid_wellknown)

    # Redis
    redis_adapter = providers.Singleton(RedisAsyncioAdapter, config.app_redis_url)

    # Fila
    alert_queue_producer = providers.Factory(RabbitMQProducer, config.app_queue_url, config.app_alert_queue_name)
    suggestion_queue_producer = providers.Factory(
        RabbitMQProducer, config.app_queue_url, config.app_price_suggestion_queue_name
    )

    # Repositórios
    price_repository = providers.Singleton(PriceRepository, sql_client)
    price_history_repository = providers.Singleton(PriceHistoryRepository, sql_client)
    alert_repository = providers.Singleton(AlertRepository, sql_client)

    # Serviços
    health_check_service = providers.Singleton(
        HealthCheckService, checkers=config.health_check_checkers, settings=settings
    )

    price_history_service = providers.Singleton(
        PriceHistoryService,
        repository=price_history_repository,
    )

    price_service = providers.Singleton(
        PriceService,
        repository=price_repository,
        redis_adapter=redis_adapter,
        alert_queue_producer=alert_queue_producer,
        suggestion_queue_producer=suggestion_queue_producer,
        price_history_repo=price_history_repository,
        price_history_service=price_history_service,
    )

    alert_service = providers.Singleton(AlertService, alert_repository=alert_repository)
