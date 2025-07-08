import pytest
from unittest.mock import AsyncMock, patch
from app.integrations.cache.redis_asyncio_adapter import RedisAsyncioAdapter


@pytest.fixture
def redis_url():
    return "redis://localhost:6379/0"


@pytest.fixture
def redis_mock():
    with patch("app.integrations.cache.redis_asyncio_adapter.Redis") as redis_cls:
        redis_instance = AsyncMock()
        redis_cls.from_url.return_value = redis_instance
        yield redis_instance


@pytest.fixture
def adapter(redis_url, redis_mock):
    return RedisAsyncioAdapter(redis_url)


@pytest.mark.asyncio
async def test_exists(adapter, redis_mock):
    redis_mock.exists.return_value = 1
    assert await adapter.exists("key") is True
    redis_mock.exists.return_value = 0
    assert await adapter.exists("key") is False


@pytest.mark.asyncio
async def test_get_str(adapter, redis_mock):
    redis_mock.get.return_value = b"abc"
    assert await adapter.get_str("key") == "abc"
    redis_mock.get.return_value = None
    assert await adapter.get_str("key") is None


@pytest.mark.asyncio
async def test_set_str_and_delete(adapter, redis_mock):
    await adapter.set_str("key", "value", 10)
    redis_mock.set.assert_awaited_with("key", "value", 10)

    await adapter.set_str("key", None)
    redis_mock.delete.assert_awaited_with("key")


@pytest.mark.asyncio
async def test_get_json(adapter, redis_mock):
    redis_mock.get.return_value = b'{"a": 1}'
    assert await adapter.get_json("key") == {"a": 1}
    redis_mock.get.return_value = None
    assert await adapter.get_json("key") is None


@pytest.mark.asyncio
async def test_set_json(adapter, redis_mock):
    await adapter.set_json("key", {"a": 1}, 5)
    redis_mock.set.assert_awaited_with("key", '{"a": 1}', 5)

    await adapter.set_json("key", None)
    redis_mock.delete.assert_awaited_with("key")


@pytest.mark.asyncio
async def test_aclose(adapter, redis_mock):
    await adapter.aclose()
    redis_mock.aclose.assert_awaited()
