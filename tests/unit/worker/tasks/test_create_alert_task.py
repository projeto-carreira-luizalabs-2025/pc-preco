import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.worker.tasks.create_alert_task import CreateAlertTask


@pytest.fixture
def alert_service():
    return AsyncMock()


@pytest.fixture
def consumer():
    mock = MagicMock()
    mock.consume = MagicMock()
    mock.close = MagicMock()
    mock.commit_message = MagicMock()
    return mock


@pytest.fixture
def task(alert_service, consumer):
    return CreateAlertTask(alert_service, consumer)


@pytest.mark.asyncio
async def test_set_running_sets_flag(task):
    await task.set_running(True)
    assert task._running is True
    await task.set_running(False)
    assert task._running is False


@pytest.mark.asyncio
async def test_close_sets_running_false_and_closes_consumer(task):
    await task.set_running(True)
    await task.close()
    assert task._running is False
    assert task.consumer is None


@pytest.mark.asyncio
async def test_process_calls_alert_service_and_commit(task, alert_service, consumer):
    message = MagicMock()
    message.value = {"foo": "bar"}
    message.has_value.return_value = True
    with patch("app.worker.tasks.create_alert_task.AlertCreate", return_value="alert_model"):
        await task.process(message)
    alert_service.create_alert.assert_awaited_once_with(alert_data="alert_model")
    consumer.commit_message.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_run_processes_message(task, consumer):
    # Simula um ciclo do loop com uma mensagem válida e depois para
    message = MagicMock()
    message.has_value.return_value = True
    consumer.consume.return_value = message

    async def stop_after_first(*args, **kwargs):
        await task.set_running(False)

    task.process = AsyncMock(side_effect=stop_after_first)

    await task.run()
    task.process.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_run_sleeps_on_empty_message(task, consumer):
    message = MagicMock()
    message.has_value.return_value = False
    consumer.consume.return_value = message

    with patch("asyncio.sleep", new_callable=AsyncMock) as sleep_mock:
        await task.set_running(True)

        # Pare o loop após a primeira chamada de sleep
        async def sleep_and_stop(*args, **kwargs):
            await task.set_running(False)

        sleep_mock.side_effect = sleep_and_stop

        await task.run()
        sleep_mock.assert_awaited()
