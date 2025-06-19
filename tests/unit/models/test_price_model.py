import pytest
from pydantic import ValidationError

from datetime import datetime

from app.models import Price


class TestPriceModel:
    def test_create_preco(self):
        """Testa a criação de uma instância de Price com os campos obrigatórios."""
        preco = Price(id=123, seller_id="1", sku="A", de=100, por=90)

        assert preco.seller_id == "1"
        assert preco.sku == "A"
        assert preco.de == 100
        assert preco.por == 90
        assert isinstance(preco.id, int)
        assert isinstance(preco.created_at, datetime)
        assert preco.updated_at is None
        assert preco.created_by is None
        assert preco.updated_by is None

    def test_update_preco(self):
        """Testa a atualização dos campos de uma instância de Price."""
        preco = Price(seller_id="1", sku="A", de=100, por=90)

        # Atualiza os campos de preço
        preco.de = 200
        preco.por = 180

        assert preco.de == 200
        assert preco.por == 180
        assert preco.seller_id == "1"  # Não alterado
        assert preco.sku == "A"  # Não alterado

    def test_from_json(self):
        """Testa a criação de uma instância de Price a partir de um JSON."""
        json_data = '{"id":123, "seller_id": "1", "sku": "A", "de": 100, "por": 90}'
        preco = Price.from_json(json_data)

        assert preco.seller_id == "1"
        assert preco.sku == "A"
        assert preco.de == 100
        assert preco.por == 90
        assert isinstance(preco.id, int)

    def test_create_preco_with_missing_fields_raises_error(self):
        """Testa se a criação de Price sem campos obrigatórios levanta erro."""
        # seller_id ausente
        with pytest.raises(ValidationError):
            Price(sku="A", de=100, por=90)
        # sku ausente
        with pytest.raises(ValidationError):
            Price(seller_id="1", de=100, por=90)
        # de ausente
        with pytest.raises(ValidationError):
            Price(seller_id="1", sku="A", por=90)
        # por ausente
        with pytest.raises(ValidationError):
            Price(seller_id="1", sku="A", de=100)

    def test_from_json_with_invalid_json_raises_error(self):
        """Testa se passar um JSON inválido para from_json levanta erro."""
        json_data = '{"seller_id": "1", "sku": "A", de="cem", por=90}'  # de inválido
        with pytest.raises(Exception):
            Price.from_json(json_data)

    def test_preco_accepts_zero_and_negative_values(self):
        """Testa se Price aceita valores zero e negativos para os preços."""
        preco = Price(seller_id="1", sku="A", de=0, por=-10)
        assert preco.de == 0
        assert preco.por == -10

    def test_preco_str_representation(self):
        """Testa se a representação em string de Price contém informações relevantes."""
        preco = Price(seller_id="1", sku="A", de=100, por=90)
        s = str(preco)
        assert "seller_id" in s or "sku" in s or "de" in s or "por" in s
