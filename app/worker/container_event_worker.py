from dependency_injector import containers, providers

from app.integrations.queue.rabbitmq_adapter import RabbitMQConsumer
from app.settings.worker import WorkerSettings

from app.integrations.database.sqlalchemy_client import SQLAlchemyClient

from app.worker.tasks.create_alert_task import CreateAlertTask
from app.services.alert_service import AlertService
from app.repositories.alert_repository import AlertRepository


class WorkerContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings = providers.Singleton(WorkerSettings)

    # -----------------------
    # ** Integrações

    sql_client = providers.Singleton(SQLAlchemyClient, config.app_db_url)

    queue_consumer = providers.Factory(RabbitMQConsumer, config.app_queue_url, config.app_queue_name)

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

    create_alert_task = providers.Singleton(CreateAlertTask, alert_service=alert_service, consumer=queue_consumer)
