import os

import dotenv
from fastapi import FastAPI

from app.container import Container
from app.settings import api_settings

ENV = os.getenv("ENV", "production")
is_dev = ENV == "dev"

dotenv.load_dotenv(override=is_dev)


def init() -> FastAPI:
    """
    Inicializa a aplicação FastAPI com as configurações e dependências necessárias.

    :return: Instância configurada da aplicação FastAPI
    """
    from app.api.api_application import create_app
    from app.api.router import routes as api_routes

    # Inicializa o container de dependências
    container = Container()
    container.config.from_pydantic(api_settings)

    # Cria a aplicação FastAPI
    app_api = create_app(api_settings, api_routes)

    # Adiciona o container à aplicação
    setattr(app_api, 'container', container)

    # Configura o autowiring para os módulos que usam injeção de dependência
    container.wire(modules=["app.api.common.routers.health_check_routers", "app.api.v1.routers.preco_router"])

    # Outros middlewares podem ser adicionados aqui se necessário

    return app_api


app = init()
