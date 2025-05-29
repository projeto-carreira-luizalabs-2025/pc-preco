# tests/test_api_main.py
import pytest
from fastapi import FastAPI
import importlib

representative_api_settings_dump = {
    "server_port": 8000,
    "openapi_path": "/openapi.json",
    "health_check_base_path": "/api",
    "cors_origins": ["*"],
    "access_log_ignored_urls": None,
    "access_log_headers_to_log": None,
    "access_log_headers_to_obfuscate": None,
    "pagination": {"default_limit": 10, "max_limit": 100},
    "filter_config": {"max_length": 100, "min_length": 1},
    "enable_seller_resources": True,
    "enable_channel_resources": True,
}


@pytest.fixture
def mock_init_dependencies(mocker):
    """
    Fixture para mockar as dependências da função init() de app/api_main.py.
    """

    # Mock para "from app.container import Container"
    mock_container_class = mocker.patch("app.api_main.Container")

    # Mock para "from app.settings import api_settings"
    mock_api_settings = mocker.patch("app.api_main.api_settings")

    # Dentro de init():
    # Mock para "from app.api.api_application import create_app"
    mock_create_app = mocker.patch("app.api.api_application.create_app")

    # Mock para "from app.api.router import router_configurations"
    mock_router_configurations = mocker.patch("app.api.router.router_configurations")

    # Configura comportamento dos mocks
    mock_container_instance = mocker.MagicMock()  # Container()
    mock_container_instance.config = mocker.MagicMock()  # config.from_dict

    # mock_container_class é a classe Container mockada
    mock_container_class.return_value = mock_container_instance

    # Return value para model_dump() é o dicionário representativo
    mock_api_settings.model_dump.return_value = representative_api_settings_dump

    # Mock que se parece com um app FastAPI
    mock_fastapi_app_instance = mocker.MagicMock(spec=FastAPI)
    mock_create_app.return_value = mock_fastapi_app_instance

    return {
        "Container": mock_container_class,
        "container_instance": mock_container_instance,
        "api_settings": mock_api_settings,
        "create_app": mock_create_app,
        "router_configurations": mock_router_configurations,
        "fastapi_app_instance": mock_fastapi_app_instance,
    }


def test_init_function_behavior(mock_init_dependencies, mocker):
    """
    Testa a lógica interna da função init() de app/api_main.py.
    """

    # Importa a função init de app.api_main.
    from app.api_main import init

    # Chama a função init()
    returned_app = init()

    # Asserções para o comportamento de init()
    mock_init_dependencies["Container"].assert_called_once()
    mock_init_dependencies["container_instance"].config.from_dict.assert_called_once_with(
        mock_init_dependencies["api_settings"].model_dump.return_value
    )
    mock_init_dependencies["create_app"].assert_called_once_with(
        mock_init_dependencies["api_settings"], mock_init_dependencies["router_configurations"]
    )
    assert returned_app == mock_init_dependencies["fastapi_app_instance"]
    assert returned_app.container == mock_init_dependencies["container_instance"]

    expected_wire_calls = [
        mocker.call(modules=["app.api.common.routers.health_check_routers"]),
        mocker.call(modules=["app.api.v1.routers.price_router"]),
        mocker.call(modules=["app.api.v2.routers.price_router"]),
    ]

    # Verifica se os métodos wire foram chamados com os módulos corretos
    mock_init_dependencies["container_instance"].wire.assert_has_calls(expected_wire_calls, any_order=False)

    # Verifica se o número de chamadas wire é igual ao esperado
    assert mock_init_dependencies["container_instance"].wire.call_count == len(expected_wire_calls)


@pytest.mark.parametrize(
    "env_value, expected_override_for_dotenv",
    [
        ("dev", True),
        ("production", False),
        ("staging", False),
    ],
)
def test_module_loading_and_global_app_initialization(mocker, env_value, expected_override_for_dotenv):
    """
    Testa a execução em nível de módulo de app/api_main.py:
    - Chamada a os.getenv("ENV", "production")
    - Chamada a dotenv.load_dotenv() com o parâmetro 'override' correto
    - Inicialização da variável global `app` através da chamada a `init()`.

    Este teste recarrega o módulo app.api_main para garantir que o código de nível superior
    seja executado com os mocks configurados para este teste específico.
    """

    # 1. Mockar dependências de nível de módulo (os.getenv, dotenv.load_dotenv)
    mock_os_getenv = mocker.patch("os.getenv", return_value=env_value)
    mock_dotenv_load = mocker.patch("dotenv.load_dotenv")

    # 2. Mockar dependências que init() usará quando `app = init()` for executado.
    mock_container_class_global = mocker.patch("app.container.Container")
    mock_api_settings_global = mocker.patch("app.settings.api_settings")

    mock_create_app_global = mocker.patch("app.api.api_application.create_app")
    mock_router_configs_global = mocker.patch("app.api.router.router_configurations")

    # Configurar comportamento dos mocks para esta chamada específica de init()
    mock_container_instance_global = mocker.MagicMock()
    mock_container_instance_global.config = mocker.MagicMock()
    mock_container_class_global.return_value = mock_container_instance_global

    mock_api_settings_global.model_dump.return_value = representative_api_settings_dump

    mock_fastapi_app_instance_global = mocker.MagicMock(spec=FastAPI)
    mock_create_app_global.return_value = mock_fastapi_app_instance_global

    # 3. Importar e recarregar `app.api_main` para disparar suas declarações de nível superior
    import app.api_main

    importlib.reload(app.api_main)  # Força a reexecução do módulo com os mocks atuais

    # 4. Asserções para a execução em nível de módulo
    mock_os_getenv.assert_called_with("ENV", "production")
    mock_dotenv_load.assert_called_once_with(override=expected_override_for_dotenv)

    # 5. Asserções para a chamada a `init()` que ocorreu para `app.api_main.app`
    mock_container_class_global.assert_called_once()
    mock_container_instance_global.config.from_dict.assert_called_once_with(
        mock_api_settings_global.model_dump.return_value
    )
    mock_create_app_global.assert_called_once_with(mock_api_settings_global, mock_router_configs_global)

    assert app.api_main.app == mock_fastapi_app_instance_global
    assert hasattr(app.api_main.app, 'container'), "A instância da app FastAPI deve ter o atributo 'container'"
    assert app.api_main.app.container == mock_container_instance_global

    expected_wire_calls_global = [
        mocker.call(modules=["app.api.common.routers.health_check_routers"]),
        mocker.call(modules=["app.api.v1.routers.price_router"]),
        mocker.call(modules=["app.api.v2.routers.price_router"]),
    ]
    mock_container_instance_global.wire.assert_has_calls(expected_wire_calls_global, any_order=False)
    assert mock_container_instance_global.wire.call_count == len(expected_wire_calls_global)
