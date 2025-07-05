import json

import pika
from pydantic import BaseModel, Field

from pclogging import LoggingBuilder

LoggingBuilder.init(log_level="WARNING")

logger = LoggingBuilder.get_logger(__name__)


class QueueMessage(BaseModel):
    ref_id: int | None = Field(None)
    value: dict | None | str = Field(None)

    def has_value(self):
        has = self.value is not None
        return has


class RabbitMQAdapter:

    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None
        self._last_mehod_frame = None

    def __del__(self):
        self.close()

    def close(self):
        if self.channel is not None:
            try:
                if getattr(self.channel, "is_open", False):
                    self.channel.close()
            except Exception as e:
                logger.error(f"Erro ao fechar o canal: {e}")
            finally:
                self.channel = None
        if self.connection is not None:
            try:
                if getattr(self.connection, "is_open", False):
                    self.connection.close()
            except Exception as e:
                logger.error(f"Erro ao fechar a conexão: {e}")
            finally:
                self.connection = None

    def connect(self):
        if self.connection is None:
            parameters = pika.URLParameters(self.amqp_url)
            self.connection = pika.BlockingConnection(parameters)
        if self.channel is None:
            self.channel = self.connection.channel()

    def create_queue(self, queue_name: str):
        self.connect()
        self.channel.queue_declare(queue=queue_name)
        self.connection.close()

    def publish_data(self, queue_name: str, message: dict):
        self.connect()
        self.channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
        self.connection.close()

    def consume_data(self, queue_name: str) -> dict:
        self.connect()
        method_frame, header_frame, body = self.channel.basic_get(queue_name, auto_ack=False)
        self._last_mehod_frame = None
        if method_frame:
            self._last_mehod_frame = method_frame
            message = json.loads(body.decode())
            return message

        return None

    def consume_message(self, queue_name: str) -> QueueMessage:
        message_data = self.consume_data(queue_name)
        ack_id = self._last_mehod_frame.delivery_tag if self._last_mehod_frame is not None else None
        message = QueueMessage(ref_id=ack_id, value=message_data)
        return message

    def delete_queue(self, queue_name: str):
        self.connect()
        self.channel.queue_delete(queue=queue_name)
        self.connection.close()

    def commit(self, delivery_tag: int):
        self.connect()
        self.channel.basic_ack(delivery_tag)

    def commit_message(self, message: QueueMessage):
        delivery_tag = message.ref_id
        if delivery_tag is None:
            raise ValueError("Sem ref_id")
        self.commit(delivery_tag)


class RabbitMQProducer(RabbitMQAdapter):

    def __init__(self, url_amqp: str, queue_name: str):
        super().__init__(url_amqp)
        self.queue_name = queue_name

    def produce(self, msg: dict):
        self.publish_data(self.queue_name, msg)


class RabbitMQConsumer(RabbitMQAdapter):
    def __init__(self, url_amqp: str, queue_name: str):
        super().__init__(url_amqp)
        self.queue_name = queue_name

    def consume(self) -> QueueMessage:
        queue_message = self.consume_message(self.queue_name)
        return queue_message
