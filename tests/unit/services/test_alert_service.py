import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.alert_service import AlertService


@pytest.fixture
def alert_repository():
    repo = AsyncMock()
    return repo


@pytest.fixture
def service(alert_repository):
    return AlertService(alert_repository)


@pytest.mark.asyncio
async def test_create_alert_calls_create(service, alert_repository):
    alert_data = MagicMock()
    alert_repository.create.return_value = "alert_obj"
    result = await service.create_alert(alert_data)
    alert_repository.create.assert_awaited_once_with(alert_data)
    assert result == "alert_obj"


@pytest.mark.asyncio
async def test_get_alerts_filters_and_calls_find(service, alert_repository):
    # Simula retorno do find
    alert_repository.find.return_value = ["alert1", "alert2"]
    paginator = MagicMock()
    filters = {"foo": "bar", "baz": None}
    result = await service.get_alerts(paginator=paginator, filters=filters)
    alert_repository.find.assert_awaited()
    assert result == ["alert1", "alert2"]
