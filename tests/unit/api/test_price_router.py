import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def recuperar_lista_precificacoes_retorna_200(client: AsyncClient):
    response = await client.get("/prices")
    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.json()


@pytest.mark.asyncio
async def recuperar_precificacao_por_seller_id_e_sku_retorna_200(client: AsyncClient):
    response = await client.get("/prices/seller123/sku456")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["seller_id"] == "seller123"
    assert response.json()["sku"] == "sku456"


@pytest.mark.asyncio
async def recuperar_precificacao_por_seller_id_e_sku_retorna_404_quando_nao_encontrado(client: AsyncClient):
    response = await client.get("/prices/seller123/sku999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def criar_precificacao_retorna_201(client: AsyncClient):
    payload = {"seller_id": "seller123", "sku": "sku456", "price": 100.0}
    response = await client.post("/prices", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["price"] == pytest.approx(100.0)


@pytest.mark.asyncio
async def criar_precificacao_retorna_400_quando_payload_invalido(client: AsyncClient):
    payload = {"seller_id": "seller123", "sku": "sku456"}
    response = await client.post("/prices", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def atualizar_precificacao_retorna_200(client: AsyncClient):
    payload = {"price": 150.0}
    response = await client.patch("/prices/seller123/sku456", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["price"] == pytest.approx(150.0)


@pytest.mark.asyncio
async def atualizar_precificacao_retorna_404_quando_nao_encontrado(client: AsyncClient):
    payload = {"price": 150.0}
    response = await client.patch("/prices/seller123/sku999", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def excluir_precificacao_retorna_204(client: AsyncClient):
    response = await client.delete("/prices/seller123/sku456")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def excluir_precificacao_retorna_404_quando_nao_encontrado(client: AsyncClient):
    response = await client.delete("/prices/seller123/sku999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
