from app.api.v1.schemas.preco_schema import PrecoCreate, PrecoResponse, PrecoSchema, PrecoUpdate


class TestPrecoSchema:
    def test_criacao_com_campos_vazios(self):
        """Testa a criação do PrecoSchema com strings vazias para seller_id e sku."""
        # Pydantic permite strings vazias por padrão
        schema = PrecoSchema(seller_id="", sku="", preco_de=10000, preco_por=8500)
        assert schema.seller_id == ""
        assert schema.sku == ""

    def test_criacao_com_precos_iguais(self):
        """Testa a criação do PrecoSchema com preco_de igual a preco_por."""
        schema = PrecoSchema(seller_id="seller123", sku="SKU001", preco_de=10000, preco_por=10000)
        assert schema.preco_de == schema.preco_por

    def test_criacao_com_precos_grandes(self):
        """Testa a criação do PrecoSchema com valores de preço muito altos."""
        schema = PrecoSchema(seller_id="seller123", sku="SKU001", preco_de=10**9, preco_por=10**8)
        assert schema.preco_de == 10**9
        assert schema.preco_por == 10**8


class TestPrecoResponse:
    def test_resposta_com_todos_os_campos_nulos(self):
        """Testa a criação do PrecoResponse com campos de auditoria nulos."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "seller_id": "seller123",
            "sku": "SKU001",
            "preco_de": 10000,
            "preco_por": 8500,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": None,
            "created_by": None,
            "updated_by": None,
        }
        response = PrecoResponse(**data)
        assert response.updated_at is None
        assert response.created_by is None
        assert response.updated_by is None

    def test_resposta_com_datas_diferentes(self):
        """Testa a criação do PrecoResponse com created_at e updated_at diferentes."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "seller_id": "seller123",
            "sku": "SKU001",
            "preco_de": 10000,
            "preco_por": 8500,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-02T00:00:00",
            "created_by": "admin",
            "updated_by": "user",
        }
        response = PrecoResponse(**data)
        assert response.created_at != response.updated_at
        assert response.created_by == "admin"
        assert response.updated_by == "user"


class TestPrecoCreate:
    def test_criacao_com_precos_minimos_validos(self):
        """Testa a criação do PrecoCreate com o menor valor válido para os preços."""
        schema = PrecoCreate(seller_id="seller123", sku="SKU001", preco_de=1, preco_por=1)
        assert schema.preco_de == 1
        assert schema.preco_por == 1


class TestPrecoUpdate:
    def test_atualizacao_com_precos_iguais(self):
        """Testa a atualização de preços com preco_de igual a preco_por."""
        schema = PrecoUpdate(preco_de=5000, preco_por=5000)
        assert schema.preco_de == schema.preco_por

    def test_atualizacao_com_precos_grandes(self):
        """Testa a atualização de preços com valores muito altos."""
        schema = PrecoUpdate(preco_de=10**9, preco_por=10**8)
        assert schema.preco_de == 10**9
        assert schema.preco_por == 10**8
