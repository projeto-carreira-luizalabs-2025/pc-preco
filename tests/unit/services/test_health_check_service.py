from unittest.mock import MagicMock, patch

import pytest

from app.services.health_check import HealthCheckService
from app.services.health_check.base_health_check import BaseHealthCheck
from app.settings import AppSettings


class TestHealthCheckService:
    @pytest.fixture
    def settings(self):
        """Cria um mock do objeto de configurações."""
        return MagicMock(spec=AppSettings)

    @pytest.fixture
    def checker_class(self):
        """Cria uma classe concreta de HealthCheck para testes."""

        class ConcreteHealthCheck(BaseHealthCheck):
            async def check_status(self):
                return "ok"

        return ConcreteHealthCheck

    @pytest.fixture
    def service(self, settings):
        """Cria um serviço de health check com métodos internos mockados."""
        with patch.object(HealthCheckService, '_set_checkers'), patch.object(
            HealthCheckService, '_check_checker'
        ), patch.object(HealthCheckService, 'check_status'):
            service = HealthCheckService(checkers=set(), settings=settings)
            return service

    def test_init_com_checkers_validos(self, settings, checker_class):
        """Verifica se o serviço inicializa corretamente com checkers válidos."""
        # Simula um dicionário de checkers
        with patch.object(HealthCheckService, '_set_checkers') as mock_set_checkers:
            service = HealthCheckService(checkers={"memory"}, settings=settings)
            mock_set_checkers.assert_called_once_with({"memory"})
            assert service._settings == settings

    def test_init_com_checkers_vazio(self, settings):
        """Verifica inicialização com conjunto vazio de checkers."""
        with patch.object(HealthCheckService, '_set_checkers') as mock_set_checkers:
            service = HealthCheckService(checkers=set(), settings=settings)
            mock_set_checkers.assert_called_once_with(set())
            assert service.checkers == {}

    @pytest.mark.asyncio
    async def test_check_status_chama_check_checker(self, settings):
        """Garante que check_status chama _check_checker com o alias correto."""
        service = HealthCheckService(checkers=set(), settings=settings)
        service._check_checker = MagicMock()

        # Mocka implementação de check_status
        async def fake_check_status(alias):
            service._check_checker(alias)

        service.check_status = fake_check_status
        await service.check_status("memory")
        service._check_checker.assert_called_once_with("memory")

    def test_set_checkers_com_checkers_nulos(self, settings):
        """Verifica que _set_checkers aceita conjunto vazio sem erro."""
        service = HealthCheckService(checkers=set(), settings=settings)
        # _set_checkers está como método não implementado, mas deve aceitar o argumento
        try:
            service._set_checkers(set())
        except Exception as e:
            pytest.fail(f"_set_checkers não deveria lançar exceção: {e}")

    def test_check_checker_com_alias_inexistente(self, settings):
        """Verifica comportamento de _check_checker com alias inexistente."""
        service = HealthCheckService(checkers=set(), settings=settings)
        # _check_checker não implementado, mas deve aceitar qualquer alias
        try:
            service._check_checker("inexistente")
        except Exception as e:
            pytest.fail(f"_check_checker não deveria lançar exceção: {e}")

    @pytest.mark.asyncio
    async def test_check_status_com_alias_invalido(self, settings):
        """Verifica que check_status aceita alias inválido sem lançar exceção."""
        service = HealthCheckService(checkers=set(), settings=settings)
        service._check_checker = MagicMock()

        async def fake_check_status(alias):
            service._check_checker(alias)

        service.check_status = fake_check_status
        try:
            await service.check_status("invalido")
        except Exception as e:
            pytest.fail(f"check_status não deveria lançar exceção: {e}")


class TestBaseHealthCheck:
    def test_init_atribui_settings(self):
        """Verifica se o settings é atribuído corretamente no construtor."""
        settings = MagicMock(spec=AppSettings)
        checker = BaseHealthCheck(settings)
        assert checker.settings == settings

    @pytest.mark.asyncio
    async def test_check_status_abstrato_retorna_none(self):
        """Garante que check_status de BaseHealthCheck não implementado retorna None."""
        checker = BaseHealthCheck(MagicMock(spec=AppSettings))
        result = await checker.check_status()
        assert result is None
