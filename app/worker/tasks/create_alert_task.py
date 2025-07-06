import asyncio

from logging import getLogger

from app.integrations.queue.rabbitmq_adapter import QueueMessage, RabbitMQConsumer

from app.api.v2.schemas.alerta_schema import AlertCreate

from app.services.alert_service import AlertService

logger = getLogger(__name__)


class CreateAlertTask:

    def __init__(self, alert_service: AlertService, consumer: RabbitMQConsumer):
        self.alert_service = alert_service
        self.consumer = consumer
        self._running = False
        self.lock = asyncio.Lock()

    async def close(self):
        async with self.lock:
            self.consumer.close()
            self._running = False
        self.consumer = None

    async def set_running(self, r: bool):
        async with self.lock:
            self._running = r

    async def run(self):
        logger.info("Executando tarefa de criacao de alerta")
        await self.set_running(True)
        while self._running:
            async with self.lock:
                message = self.consumer.consume()
            if message.has_value():
                await self.process(message)
            else:
                # XXX Exportar o tempo para variável
                await asyncio.sleep(1)

    async def process(self, message: QueueMessage):
        alerta_data = message.value
        alert_model = AlertCreate(**alerta_data)

        await self.alert_service.create_alert(alert_data=alert_model)

        self.consumer.commit_message(message)
