import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.worker.tasks.suggest_price_task import SuggestPriceTask


@pytest.fixture
def redis_adapter():
    mock = AsyncMock()
    mock.set_json = AsyncMock()
    return mock


@pytest.fixture
def consumer():
    mock = MagicMock()
    mock.consume = MagicMock()
    mock.close = MagicMock()
    mock.commit_message = MagicMock()
    return mock


@pytest.fixture
def task(redis_adapter, consumer):
    return SuggestPriceTask(redis_adapter, consumer, ia_api_url="http://fake-ia", ia_model="fake-model")


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
async def test_process_sets_cache_and_commits(task, redis_adapter, consumer):
    message = MagicMock()
    message.value = {"job_id": "123", "foo": "bar"}
    message.has_value.return_value = True
    task.generate_price_suggestion = AsyncMock(return_value="42.0")
    await task.process(message)
    redis_adapter.set_json.assert_awaited_with(
        "suggestion:123", {"status": "done", "suggested_price": "42.0"}, expires_in_seconds=300
    )
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


@pytest.mark.asyncio
async def test_generate_price_suggestion_success(task):
    data = {"seller_id": "1", "sku": "A", "history": [10, 20]}
    fake_response = {"response": "99.99"}
    with patch("httpx.AsyncClient") as client_mock:
        client_instance = client_mock.return_value
        client_instance.__aenter__.return_value = client_instance
        client_instance.post = AsyncMock()
        client_instance.post.return_value.json = AsyncMock(return_value=fake_response)
        client_instance.post.return_value.raise_for_status = MagicMock()
        result = await task.generate_price_suggestion(data)
        assert result == "99.99"
