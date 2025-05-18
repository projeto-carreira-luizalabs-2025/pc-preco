from datetime import datetime, timezone

from app.common.datetime import utcnow


class TestDatetime:
    def test_utcnow(self):
        """Testa se utcnow retorna um datetime com timezone UTC."""
        now = utcnow()

        assert isinstance(now, datetime)
        assert now.tzinfo == timezone.utc

        # Verifica se o horário está próximo do atual (até 1 segundo de diferença)
        current_time = datetime.now(timezone.utc)
        time_diff = (current_time - now).total_seconds()
        assert abs(time_diff) < 1

    def test_utcnow_trunca_microssegundos(self):
        """Garante que utcnow trunca os microssegundos para múltiplos de milissegundos."""
        now = utcnow()
        # O valor dos microssegundos deve ser múltiplo de 1000 (milissegundos)
        assert now.microsecond % 1000 == 0

    def test_utcnow_nao_retorna_naive(self):
        """Verifica que utcnow nunca retorna um datetime 'naive' (sem timezone)."""
        now = utcnow()
        assert now.tzinfo is not None

    def test_utcnow_mudanca_de_segundo(self):
        """Testa o comportamento de utcnow próximo à virada de segundo."""
        # Chama utcnow duas vezes rapidamente e garante que a diferença é pequena
        now1 = utcnow()
        now2 = utcnow()
        diff = abs((now2 - now1).total_seconds())
        # A diferença deve ser muito pequena, pois as chamadas são quase simultâneas
        assert diff < 0.01
