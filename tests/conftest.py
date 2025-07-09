from glob import glob

from dotenv import load_dotenv

# Configura ambiente de testes
load_dotenv()

import pytest

from app.api.common.auth_handler import do_auth
from app.api_main import app
from app.repositories import PriceRepository
from tests.factories.price_repository_mock_factory import PriceRepositoryMockFactory

# Carregando as fixtures dinamicamente


def refactor_fixture_path(string: str) -> str:
    return string.replace("/", ".").replace("\\", ".").replace(".py", "")


pytest_plugins = [
    refactor_fixture_path(fixture) for fixture in glob("tests/fixtures/**/*.py", recursive=True) if "__" not in fixture
]
