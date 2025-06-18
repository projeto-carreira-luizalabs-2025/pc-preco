from fastapi import FastAPI

from app.api.api_application import create_app
from app.api.router import router_configurations
from app.settings import api_settings


def test_criacao_app_fastapi():
    app = create_app(api_settings, router_configurations)
    assert isinstance(app, FastAPI)
    assert getattr(app, "title", None) == api_settings.app_name
    openapi_schema = getattr(app, "openapi_schema", None) or app.openapi()
    assert openapi_schema["openapi"] == "3.0.2"
    assert getattr(app, "version", None) == api_settings.version


def test_rotas_incluidas():
    app = create_app(api_settings, router_configurations)
    urls = [getattr(route, "path", None) for route in getattr(app, "routes", [])]
    # Verifica se as rotas principais estão presentes
    assert any("/api/v2" in str(url) for url in urls)
