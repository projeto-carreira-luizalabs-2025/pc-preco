from dependency_injector import containers, providers

from app.integrations.cache.redis_asyncio_adapter import RedisAsyncioAdapter
from app.integrations.database.sqlalchemy_client import SQLAlchemyClient
from app.integrations.queue.rabbitmq_adapter import RabbitMQConsumer
from app.repositories.alert_repository import AlertRepository
from app.services.alert_service import AlertService
from app.settings.worker import WorkerSettings
from app.worker.tasks.create_alert_task import CreateAlertTask
from app.worker.tasks.suggest_price_task import SuggestPriceTask


class WorkerContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings = providers.Singleton(WorkerSettings)

    # -----------------------
    # ** Integrações

    sql_client = providers.Singleton(SQLAlchemyClient, config.app_db_url)

    redis_adapter = providers.Singleton(RedisAsyncioAdapter, config.app_redis_url)

    alert_queue_consumer = providers.Factory(RabbitMQConsumer, config.app_queue_url, config.app_alert_queue_name)
    suggestion_queue_consumer = providers.Factory(
        RabbitMQConsumer, config.app_queue_url, config.app_price_suggestion_queue_name
    )

    # -----------------------
    # ** Repositórios
    #

    alert_repository = providers.Singleton(AlertRepository, sql_client=sql_client)

    # Repositório de alertas

    # -----------------------
    # ** Servicos
    #

    alert_service = providers.Singleton(AlertService, alert_repository=alert_repository)

    # Trabalhando com fila

    # Aqui vai estar o serviço que consome a fila e processa as mensagens

    # -----------------------
    # ** tarefas
    #

    create_alert_task = providers.Singleton(CreateAlertTask, alert_service=alert_service, consumer=alert_queue_consumer)
    suggest_price_task = providers.Singleton(
        SuggestPriceTask,
        redis_adapter=redis_adapter,
        consumer=suggestion_queue_consumer,
        ia_api_url=config.ia_api_url,
        ia_model=config.ia_model,
    )
