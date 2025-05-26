from contextlib import asynccontextmanager
from enum import Enum
from typing import List, Optional, Tuple, Union

from fastapi import APIRouter, FastAPI

from app.settings import ApiSettings

from .common.error_handlers import add_error_handlers
from .common.routers.health_check_routers import add_health_check_router
from .middlewares.configure_middlewares import configure_middlewares


def create_app(
    settings: ApiSettings, router_configs: List[Tuple[APIRouter, str, Optional[List[Union[str, Enum]]]]]
) -> FastAPI:
    @asynccontextmanager
    async def _lifespan(_app: FastAPI):
        # Qualquer ação necessária na inicialização
        ...
        yield
        # Limpando a bagunça antes de terminar
        ...

    app = FastAPI(
        lifespan=_lifespan,
        title=settings.app_name,
        description="""
        # API de Precificação

        API para gerenciamento de preços de produtos por seller.

        ## Funcionalidades

        * Consulta de preços por seller e SKU
        * Criação de novas precificações
        * Atualização de preços existentes
        * Exclusão de precificações

        ## Observações

        * Todos os valores monetários são representados em centavos (ex: R$ 100,00 = 10000)
        * A API suporta paginação, ordenação e filtragem nas consultas
        """,
        openapi_url=settings.openapi_path,
        version=settings.version,
        docs_url="/api/docs",
    )
    # Para garantir compatibilidade com o kong não podemos usar recursos acima da versão 3.0.2
    app.openapi_version = "3.0.2"

    # Configurações Gerais
    configure_middlewares(app, settings)

    add_error_handlers(app)

    # Rotas
    for router_instance, prefix, tags in router_configs:
        app.include_router(router_instance, prefix=prefix, tags=tags)

    add_health_check_router(app, prefix=settings.health_check_base_path)

    return app
