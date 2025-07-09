from app.worker.container_event_worker import WorkerContainer


def test_worker_container_providers():
    container = WorkerContainer()
    # Testa se os providers principais existem e podem ser criados
    assert container.sql_client is not None
    assert container.redis_adapter is not None
    assert container.alert_queue_consumer is not None
    assert container.suggestion_queue_consumer is not None
    assert container.alert_repository is not None
    assert container.alert_service is not None
    assert container.create_alert_task is not None
    assert container.suggest_price_task is not None


def test_worker_container_config():
    container = WorkerContainer()
    # Testa se o config pode ser setado
    container.config.app_db_url.from_env("APP_DB_URL")
    container.config.app_redis_url.from_env("APP_REDIS_URL")
    container.config.app_queue_url.from_env("APP_QUEUE_URL")
    container.config.app_alert_queue_name.from_env("APP_ALERT_QUEUE_NAME")
    container.config.app_price_suggestion_queue_name.from_env("APP_PRICE_SUGGESTION_QUEUE_NAME")
    container.config.ia_api_url.from_env("IA_API_URL")
    container.config.ia_model.from_env("IA_MODEL")
