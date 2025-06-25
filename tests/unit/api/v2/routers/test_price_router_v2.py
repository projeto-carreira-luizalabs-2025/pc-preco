import pytest
from httpx import AsyncClient
import pytest_asyncio


@pytest.mark.usefixtures("mock_do_auth", "async_client")
class TestPriceRouterV2:
    @pytest.mark.asyncio
    async def test_listar_precos(self, async_client: AsyncClient):
        resposta = await async_client.get("/api/v2/precos", headers={"x-seller-id": "1"})
        assert resposta.status_code == 200
        assert "results" in resposta.json()

    @pytest.mark.asyncio
    async def test_buscar_preco_por_sku(self, async_client: AsyncClient, test_prices):
        preco = test_prices[0]
        resposta = await async_client.get(f"/api/v2/precos/{preco.sku}", headers={"x-seller-id": preco.seller_id})
        assert resposta.status_code == 200
        assert resposta.json()["seller_id"] == preco.seller_id
        assert resposta.json()["sku"] == preco.sku

    @pytest.mark.asyncio
    async def test_criar_preco(self, async_client: AsyncClient):
        novo_preco = {"seller_id": "3", "sku": "C", "de": 300, "por": 250}
        resposta = await async_client.post("/api/v2/precos", json=novo_preco, headers={"x-seller-id": "3"})
        assert resposta.status_code == 201
        assert resposta.json()["seller_id"] == "3"
        assert resposta.json()["sku"] == "C"

    @pytest.mark.asyncio
    async def test_atualizar_preco(self, async_client: AsyncClient, test_prices):
        preco = test_prices[0]
        update = {"de": 120, "por": 110}
        resposta = await async_client.put(
            f"/api/v2/precos/{preco.sku}", json=update, headers={"x-seller-id": preco.seller_id}
        )
        assert resposta.status_code == 200
        assert resposta.json()["de"] == 120
        assert resposta.json()["por"] == 110

    @pytest.mark.asyncio
    async def test_patch_preco(self, async_client: AsyncClient, test_prices):
        preco = test_prices[0]
        patch = {"por": 95}
        resposta = await async_client.patch(
            f"/api/v2/precos/{preco.sku}", json=patch, headers={"x-seller-id": preco.seller_id}
        )
        assert resposta.status_code == 200
        assert resposta.json()["por"] == 95

    @pytest.mark.asyncio
    async def test_deletar_preco(self, async_client: AsyncClient, test_prices):
        preco = test_prices[0]
        resposta = await async_client.delete(f"/api/v2/precos/{preco.sku}", headers={"x-seller-id": preco.seller_id})
        assert resposta.status_code == 204
