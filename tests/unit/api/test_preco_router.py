import os
import sys
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.api.v1.schemas.preco_schema import PrecoUpdate
from app.common.exceptions import BadRequestException, NotFoundException
from app.models import Preco
from app.services import PrecoService


class TestPrecoRouter:
    @pytest.fixture
    def preco_service_mock(self):
        service = AsyncMock(spec=PrecoService)

        # Mock para busca paginada de preços
        async def find(paginator, filters):
            return [
                Preco(
                    id=UUID("00000000-0000-0000-0000-000000000001"), seller_id="1", sku="A", preco_de=100, preco_por=90
                ),
                Preco(
                    id=UUID("00000000-0000-0000-0000-000000000002"), seller_id="2", sku="B", preco_de=200, preco_por=180
                ),
            ]

        service.find.side_effect = find

        # Mock para busca por seller_id e sku
        async def find_by_seller_id_and_sku(seller_id, sku):
            if seller_id == "1" and sku == "A":
                return Preco(
                    id=UUID("00000000-0000-0000-0000-000000000001"), seller_id="1", sku="A", preco_de=100, preco_por=90
                )
            raise NotFoundException()

        service.find_by_seller_id_and_sku.side_effect = find_by_seller_id_and_sku

        # Mock para criação de preço
        async def create_preco(preco_create):
            if preco_create.seller_id == "1" and preco_create.sku == "A":
                raise BadRequestException()
            return Preco(
                id=UUID("00000000-0000-0000-0000-000000000003"),
                seller_id=preco_create.seller_id,
                sku=preco_create.sku,
                preco_de=preco_create.preco_de,
                preco_por=preco_create.preco_por,
            )

        service.create_preco.side_effect = create_preco

        # Mock para atualização de preço
        async def update_preco(seller_id, sku, preco_update):
            if seller_id == "1" and sku == "A":
                return Preco(
                    id=UUID("00000000-0000-0000-0000-000000000001"),
                    seller_id="1",
                    sku="A",
                    preco_de=preco_update.preco_de,
                    preco_por=preco_update.preco_por,
                )
            raise NotFoundException()

        service.update_preco.side_effect = update_preco

        # Mock para deleção de preço
        async def delete_by_seller_id_and_sku(seller_id, sku):
            if seller_id != "1" or sku != "A":
                raise NotFoundException()
            return None

        service.delete_by_seller_id_and_sku.side_effect = delete_by_seller_id_and_sku

        return service

    @pytest.fixture
    def app(self):
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
        from app.api_main import app as fastapi_app

        return fastapi_app

    @pytest.fixture
    def client(self, app, preco_service_mock):
        app.container.preco_service.override(preco_service_mock)
        return TestClient(app)

    def test_get_precos(self, client, preco_service_mock):
        response = client.get("/seller/v1/precos")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
        assert data["results"][0]["seller_id"] == "1"
        assert data["results"][0]["sku"] == "A"
        assert data["results"][1]["seller_id"] == "2"
        assert data["results"][1]["sku"] == "B"
        preco_service_mock.find.assert_called_once()

    def test_get_preco_by_seller_id_and_sku_found(self, client, preco_service_mock):
        response = client.get("/seller/v1/precos/1/A")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["seller_id"] == "1"
        assert data["sku"] == "A"
        assert data["preco_de"] == 100
        assert data["preco_por"] == 90
        preco_service_mock.find_by_seller_id_and_sku.assert_called_once_with(seller_id="1", sku="A")

    def test_get_preco_by_seller_id_and_sku_not_found(self, client, preco_service_mock):
        response = client.get("/seller/v1/precos/2/B")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        preco_service_mock.find_by_seller_id_and_sku.assert_called_once_with(seller_id="2", sku="B")

    def test_create_preco_success(self, client, preco_service_mock):
        preco_data = {"seller_id": "3", "sku": "C", "preco_de": 300, "preco_por": 270}
        response = client.post("/seller/v1/precos", json=preco_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["seller_id"] == "3"
        assert data["sku"] == "C"
        assert data["preco_de"] == 300
        assert data["preco_por"] == 270
        preco_service_mock.create_preco.assert_called_once()

    def test_create_preco_already_exists(self, client, preco_service_mock):
        preco_data = {"seller_id": "1", "sku": "A", "preco_de": 100, "preco_por": 90}
        response = client.post("/seller/v1/precos", json=preco_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        preco_service_mock.create_preco.assert_called_once()

    def test_update_preco_success(self, client, preco_service_mock):
        preco_data = {"preco_de": 150, "preco_por": 120}
        response = client.patch("/seller/v1/precos/1/A", json=preco_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["seller_id"] == "1"
        assert data["sku"] == "A"
        assert data["preco_de"] == 150
        assert data["preco_por"] == 120
        preco_service_mock.update_preco.assert_called_once()
        args, kwargs = preco_service_mock.update_preco.call_args
        assert args[0] == "1"
        assert args[1] == "A"
        assert isinstance(args[2], PrecoUpdate)
        assert args[2].preco_de == 150
        assert args[2].preco_por == 120

    def test_update_preco_not_found(self, client, preco_service_mock):
        preco_data = {"preco_de": 150, "preco_por": 120}
        response = client.patch("/seller/v1/precos/2/B", json=preco_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        preco_service_mock.update_preco.assert_called_once()

    def test_delete_preco_success(self, client, preco_service_mock):
        response = client.delete("/seller/v1/precos/1/A")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        preco_service_mock.delete_by_seller_id_and_sku.assert_called_once_with("1", "A")

    def test_delete_preco_not_found(self, client, preco_service_mock):
        response = client.delete("/seller/v1/precos/2/B")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        preco_service_mock.delete_by_seller_id_and_sku.assert_called_once_with("2", "B")

    def test_create_preco_valores_invalidos(self, client, preco_service_mock):
        preco_data = {"seller_id": "4", "sku": "D", "preco_de": -10, "preco_por": 0}
        response = client.post("/seller/v1/precos", json=preco_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_preco_valores_invalidos(self, client, preco_service_mock):
        preco_data = {"preco_de": 0, "preco_por": -50}
        response = client.patch("/seller/v1/precos/1/A", json=preco_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_precos_empty(self, client, preco_service_mock):
        async def empty_find(paginator, filters):
            return []

        preco_service_mock.find.side_effect = empty_find
        response = client.get("/seller/v1/precos")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
        assert data["results"] == []
        preco_service_mock.find.assert_called_once()
