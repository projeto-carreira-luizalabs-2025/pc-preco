from unittest.mock import MagicMock

import pytest

from app.api.common.injector import get_seller_id
from app.common.exceptions import BadRequestException


@pytest.mark.asyncio
async def test_get_seller_id_success():
    request = MagicMock()
    request.headers.get.return_value = "123"
    result = await get_seller_id(request)
    assert result == "123"


@pytest.mark.asyncio
async def test_get_seller_id_missing():
    request = MagicMock()
    request.headers.get.return_value = None
    with pytest.raises(BadRequestException) as exc:
        await get_seller_id(request)
    assert exc.value.status_code == 400
