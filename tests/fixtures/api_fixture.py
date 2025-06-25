from pytest import fixture

from fastapi.testclient import TestClient
from typing import Generator

from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport


@fixture
def client(app) -> Generator[TestClient, None, None]:
    with TestClient(app) as client_instance:
        yield client_instance


@fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
