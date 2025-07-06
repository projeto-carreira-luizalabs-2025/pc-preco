"""
Script para criar fila da aplicação.
"""

from app.settings import AppSettings
from app.integrations.queue.rabbitmq_adapter import RabbitMQAdapter, RabbitMQConsumer, RabbitMQProducer
from datetime import datetime


def produce_consume(app_settings: AppSettings):
    producer = RabbitMQProducer(app_settings.app_queue_url, app_settings.app_queue_name)
    info = {"data": datetime.now().isoformat(), "info": "teste"}
    print("Publicando: ", info)
    producer.publish_message(app_settings.app_queue_name, info)

    consumer = RabbitMQConsumer(app_settings.app_queue_url, app_settings.app_queue_name)
    message = consumer.consume()
    print("Consumindo: ", message)


def create_queue():
    """
    Cria fila da aplicação.
    """
    app_settings = AppSettings()

    queue_name = app_settings.app_queue_name
    print("Criando a fila", queue_name)

    rabbitmq_adapter = RabbitMQAdapter(app_settings.app_queue_url)
    rabbitmq_adapter.create_queue(queue_name)
    print("Fila criada!")


if __name__ == "__main__":
    create_queue()
