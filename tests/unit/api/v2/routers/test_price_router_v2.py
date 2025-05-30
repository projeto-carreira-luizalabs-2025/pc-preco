import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("client")
class TestPriceRouterV2:
    def test_listar_precos(self, client: TestClient):
        resposta = client.get("/api/v2/precos", headers={"seller-id": "1"})
        assert resposta.status_code == 200
        assert "results" in resposta.json()

    def test_buscar_preco_por_sku(self, client: TestClient, test_prices):
        preco = test_prices[0]
        resposta = client.get(f"/api/v2/precos/{preco.sku}", headers={"seller-id": preco.seller_id})
        assert resposta.status_code == 200
        assert resposta.json()["seller_id"] == preco.seller_id
        assert resposta.json()["sku"] == preco.sku

    def test_criar_preco(self, client: TestClient):
        novo_preco = {"seller_id": "3", "sku": "C", "de": 300, "por": 250}
        resposta = client.post("/api/v2/precos", json=novo_preco, headers={"seller-id": "3"})
        assert resposta.status_code == 201
        assert resposta.json()["seller_id"] == "3"
        assert resposta.json()["sku"] == "C"

    def test_atualizar_preco(self, client: TestClient, test_prices):
        preco = test_prices[0]
        update = {"de": 120, "por": 110}
        resposta = client.put(f"/api/v2/precos/{preco.sku}", json=update, headers={"seller-id": preco.seller_id})
        assert resposta.status_code == 200
        assert resposta.json()["de"] == 120
        assert resposta.json()["por"] == 110

    def test_patch_preco(self, client: TestClient, test_prices):
        preco = test_prices[0]
        patch = {"por": 95}
        resposta = client.patch(f"/api/v2/precos/{preco.sku}", json=patch, headers={"seller-id": preco.seller_id})
        assert resposta.status_code == 200
        assert resposta.json()["por"] == 95

    def test_deletar_preco(self, client: TestClient, test_prices):
        preco = test_prices[0]
        resposta = client.delete(f"/api/v2/precos/{preco.sku}", headers={"seller-id": preco.seller_id})
        assert resposta.status_code == 204
