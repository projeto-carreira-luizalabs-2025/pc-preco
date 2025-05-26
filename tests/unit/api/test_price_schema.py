from app.api.common.schemas.price.price_schema import PriceCreate, PriceResponse, PriceSchema, PriceUpdate


class TestPrecoSchema:
    def test_criacao_com_campos_vazios(self):
        """Testa a criação do PriceSchema com strings vazias para seller_id e sku."""
        schema = PriceSchema(seller_id="", sku="", de=10000, por=8500)
        assert schema.seller_id == ""
        assert schema.sku == ""

    def test_criacao_com_precos_iguais(self):
        """Testa a criação do PriceSchema com o atributo 'de' igual ao atributo 'por'."""
        schema = PriceSchema(seller_id="seller123", sku="SKU001", de=10000, por=10000)
        assert schema.de == schema.por

    def test_criacao_com_precos_grandes(self):
        """Testa a criação do PriceSchema com valores de preço muito altos."""
        schema = PriceSchema(seller_id="seller123", sku="SKU001", de=10**9, por=10**8)
        assert schema.de == 10**9
        assert schema.por == 10**8


class TestPrecoResponse:
    def test_resposta_com_todos_os_campos_nulos(self):
        """Testa a criação do PriceResponse com campos de auditoria nulos."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "seller_id": "seller123",
            "sku": "SKU001",
            "de": 10000,
            "por": 8500,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": None,
            "created_by": None,
            "updated_by": None,
        }
        response = PriceResponse(**data)
        assert response.updated_at is None
        assert response.created_by is None
        assert response.updated_by is None

    def test_resposta_com_datas_diferentes(self):
        """Testa a criação do PriceResponse com created_at e updated_at diferentes."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "seller_id": "seller123",
            "sku": "SKU001",
            "de": 10000,
            "por": 8500,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-02T00:00:00",
            "created_by": "admin",
            "updated_by": "user",
        }
        response = PriceResponse(**data)
        assert response.created_at != response.updated_at
        assert response.created_by == "admin"
        assert response.updated_by == "user"


class TestPrecoCreate:
    def test_criacao_com_precos_minimos_validos(self):
        """Testa a criação do PriceCreate com o menor valor válido para os preços."""
        schema = PriceCreate(seller_id="seller123", sku="SKU001", de=1, por=1)
        assert schema.de == 1
        assert schema.por == 1


class TestPrecoUpdate:
    def test_atualizacao_com_precos_iguais(self):
        """Testa a atualização de preços com o atributo 'de' igual ao atributo 'por'."""
        schema = PriceUpdate(de=5000, por=5000)
        assert schema.de == schema.por

    def test_atualizacao_com_precos_grandes(self):
        """Testa a atualização de preços com valores muito altos."""
        schema = PriceUpdate(de=10**9, por=10**8)
        assert schema.de == 10**9
        assert schema.por == 10**8
