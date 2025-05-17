from dependency_injector import containers, providers

from app.models import Preco
from app.repositories import PrecoRepository
from app.services import HealthCheckService, PrecoService
from app.settings import AppSettings

# Dados iniciais para o repositório em memória
memory_precos = [
    Preco(seller_id="1", sku="A", preco_de=100, preco_por=90),
    Preco(seller_id="2", sku="B", preco_de=200, preco_por=180),
]


class Container(containers.DeclarativeContainer):
    """
    Container de injeção de dependências da aplicação.
    Configura e fornece todas as dependências necessárias para os serviços.
    """
    # Configuração
    config = providers.Configuration()

    # Configurações da aplicação
    settings = providers.Singleton(AppSettings)

    # Repositórios
    preco_repository = providers.Singleton(
        PrecoRepository, 
        memory=memory_precos
    )

    # Serviços
    health_check_service = providers.Singleton(
        HealthCheckService, 
        checkers=config.health_check_checkers, 
        settings=settings
    )

    preco_service = providers.Singleton(
        PrecoService, 
        repository=preco_repository
    )
