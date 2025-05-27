import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("client")
class TestPriceRouterV1:
    def test_listar_precos(self, client: TestClient):
        resposta = client.get("/api/v1/precos")
        assert resposta.status_code == 200
        assert "results" in resposta.json()

    def test_buscar_preco_por_seller_e_sku(self, client: TestClient, test_prices):
        preco = test_prices[0]
        resposta = client.get(f"/api/v1/precos/{preco.seller_id}/{preco.sku}")
        assert resposta.status_code == 200
        assert resposta.json()["seller_id"] == preco.seller_id
        assert resposta.json()["sku"] == preco.sku

    def test_criar_preco(self, client: TestClient):
        novo_preco = {"seller_id": "3", "sku": "C", "de": 300, "por": 250}
        resposta = client.post("/api/v1/precos", json=novo_preco)
        assert resposta.status_code == 201
        assert resposta.json()["seller_id"] == "3"
        assert resposta.json()["sku"] == "C"

    def test_atualizar_preco(self, client: TestClient, test_prices):
        preco = test_prices[0]
        update = {"de": 120, "por": 110}
        resposta = client.put(f"/api/v1/precos/{preco.seller_id}/{preco.sku}", json=update)
        assert resposta.status_code == 200
        assert resposta.json()["de"] == 120
        assert resposta.json()["por"] == 110

    def test_patch_preco(self, client: TestClient, test_prices):
        preco = test_prices[0]
        patch = {"por": 95}
        resposta = client.patch(f"/api/v1/precos/{preco.seller_id}/{preco.sku}", json=patch)
        assert resposta.status_code == 200
        assert resposta.json()["por"] == 95

    def test_deletar_preco(self, client: TestClient, test_prices):
        preco = test_prices[0]
        resposta = client.delete(f"/api/v1/precos/{preco.seller_id}/{preco.sku}")
        assert resposta.status_code == 204
