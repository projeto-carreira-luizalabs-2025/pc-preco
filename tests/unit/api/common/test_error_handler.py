import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from app.api.common.error_handlers import add_error_handlers
from app.common.exceptions import ApplicationException
from app.common.error_codes import ErrorInfo


def test_http_exception_handler():
    app = FastAPI()
    add_error_handlers(app)

    @app.get("/raise-http")
    async def raise_http():
        raise HTTPException(status_code=418, detail="teapot")

    client = TestClient(app)
    response = client.get("/raise-http")
    assert response.status_code == 418
    assert response.json()["slug"] == "INTERNAL_SERVER_ERROR"


def test_application_exception_handler():
    app = FastAPI()
    add_error_handlers(app)

    @app.get("/raise-app")
    async def raise_app():
        error_info = ErrorInfo(slug="dummy", message="fail", http_code=422)
        raise ApplicationException(error_info=error_info)

    client = TestClient(app)
    response = client.get("/raise-app")
    assert response.status_code == 422


def test_default_exception_handler():
    app = FastAPI()
    add_error_handlers(app)

    @app.get("/raise-exc")
    async def raise_exc():
        raise RuntimeError("fail")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/raise-exc")
    assert response.status_code == 500
    assert response.json()["slug"] == "INTERNAL_SERVER_ERROR"
