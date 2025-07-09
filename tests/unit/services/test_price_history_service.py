from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.exceptions.price_exceptions import PriceNotFoundException
from app.services.price_history_service import PriceHistoryService


@pytest.fixture
def repository():
    return AsyncMock()


@pytest.fixture
def service(repository):
    return PriceHistoryService(repository)


@pytest.mark.asyncio
async def test_get_by_seller_id_and_sku_success(service, repository):
    paginator = MagicMock()
    fake_history = [MagicMock(), MagicMock()]
    repository.find.return_value = fake_history
    result = await service.get_by_seller_id_and_sku("1", "A", paginator)
    repository.find.assert_awaited()
    assert result == fake_history


@pytest.mark.asyncio
async def test_get_by_seller_id_and_sku_not_found(service, repository):
    paginator = MagicMock()
    repository.find.return_value = []
    with pytest.raises(PriceNotFoundException):
        await service.get_by_seller_id_and_sku("1", "A", paginator)


@pytest.mark.asyncio
async def test_get_last_n_prices_success(service, repository):
    fake_history = [MagicMock(), MagicMock()]
    repository.find.return_value = fake_history
    result = await service.get_last_n_prices("1", "A", n=2)
    repository.find.assert_awaited()
    assert result == fake_history


@pytest.mark.asyncio
async def test_get_last_n_prices_not_found(service, repository):
    repository.find.return_value = []
    with pytest.raises(PriceNotFoundException):
        await service.get_last_n_prices("1", "A", n=2)
