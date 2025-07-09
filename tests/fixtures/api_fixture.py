from typing import AsyncGenerator, Generator

from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from pytest import fixture


@fixture
def client(app) -> Generator[TestClient, None, None]:
    with TestClient(app) as client_instance:
        yield client_instance


@fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
