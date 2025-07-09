from unittest.mock import MagicMock, call, patch

import pytest

from app.integrations.queue.rabbitmq_adapter import QueueMessage, RabbitMQAdapter


@pytest.fixture
def amqp_url():
    return "amqp://guest:guest@localhost:5672/"


@pytest.fixture
def pika_mock():
    with patch("app.integrations.queue.rabbitmq_adapter.pika") as pika_mod:
        yield pika_mod


@pytest.fixture
def adapter(amqp_url, pika_mock):
    return RabbitMQAdapter(amqp_url)


def test_connect_creates_connection_and_channel(adapter, pika_mock):
    connection_mock = MagicMock()
    channel_mock = MagicMock()
    pika_mock.BlockingConnection.return_value = connection_mock
    connection_mock.channel.return_value = channel_mock

    adapter.connect()
    assert adapter.connection == connection_mock
    assert adapter.channel == channel_mock


def test_create_queue(adapter, pika_mock):
    channel_mock = MagicMock()
    connection_mock = MagicMock()
    pika_mock.BlockingConnection.return_value = connection_mock
    connection_mock.channel.return_value = channel_mock

    adapter.create_queue("test-queue")
    channel_mock.queue_declare.assert_called_once_with(queue="test-queue")
    channel_mock.close.assert_called_once()
    connection_mock.close.assert_called_once()
    assert adapter.channel is None
    assert adapter.connection is None


def test_publish_data(adapter, pika_mock):
    channel_mock = MagicMock()
    connection_mock = MagicMock()
    pika_mock.BlockingConnection.return_value = connection_mock
    connection_mock.channel.return_value = channel_mock

    adapter.publish_data("queue", {"foo": "bar"})
    channel_mock.basic_publish.assert_called_once()
    channel_mock.close.assert_called_once()
    connection_mock.close.assert_called_once()
    assert adapter.channel is None
    assert adapter.connection is None


def test_consume_data_returns_message(adapter, pika_mock):
    channel_mock = MagicMock()
    connection_mock = MagicMock()
    pika_mock.BlockingConnection.return_value = connection_mock
    connection_mock.channel.return_value = channel_mock

    method_frame = MagicMock()
    method_frame.delivery_tag = 123
    body = b'{"foo": "bar"}'
    channel_mock.basic_get.return_value = (method_frame, None, body)

    result = adapter.consume_data("queue")
    assert result == {"foo": "bar"}
    assert adapter._last_mehod_frame == method_frame


def test_consume_data_returns_none(adapter, pika_mock):
    channel_mock = MagicMock()
    connection_mock = MagicMock()
    pika_mock.BlockingConnection.return_value = connection_mock
    connection_mock.channel.return_value = channel_mock

    channel_mock.basic_get.return_value = (None, None, None)
    result = adapter.consume_data("queue")
    assert result is None


def test_consume_message(adapter, pika_mock):
    channel_mock = MagicMock()
    connection_mock = MagicMock()
    pika_mock.BlockingConnection.return_value = connection_mock
    connection_mock.channel.return_value = channel_mock

    method_frame = MagicMock()
    method_frame.delivery_tag = 42
    body = b'{"foo": "bar"}'
    channel_mock.basic_get.return_value = (method_frame, None, body)

    msg = adapter.consume_message("queue")
    assert isinstance(msg, QueueMessage)
    assert msg.ref_id == 42
    assert msg.value == {"foo": "bar"}


def test_delete_queue(adapter, pika_mock):
    channel_mock = MagicMock()
    connection_mock = MagicMock()
    pika_mock.BlockingConnection.return_value = connection_mock
    connection_mock.channel.return_value = channel_mock

    adapter.delete_queue("queue")
    channel_mock.queue_delete.assert_called_once_with(queue="queue")
    channel_mock.close.assert_called_once()
    connection_mock.close.assert_called_once()
    assert adapter.channel is None
    assert adapter.connection is None


def test_commit(adapter, pika_mock):
    channel_mock = MagicMock()
    connection_mock = MagicMock()
    pika_mock.BlockingConnection.return_value = connection_mock
    connection_mock.channel.return_value = channel_mock

    adapter.commit(123)
    channel_mock.basic_ack.assert_called_once_with(123)


def test_commit_message(adapter, pika_mock):
    channel_mock = MagicMock()
    connection_mock = MagicMock()
    pika_mock.BlockingConnection.return_value = connection_mock
    connection_mock.channel.return_value = channel_mock

    msg = QueueMessage(ref_id=99, value={"foo": "bar"})
    adapter.commit_message(msg)
    channel_mock.basic_ack.assert_called_once_with(99)


def test_commit_message_without_ref_id(adapter):
    msg = QueueMessage(ref_id=None, value={"foo": "bar"})
    with pytest.raises(ValueError):
        adapter.commit_message(msg)
