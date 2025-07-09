import pytest

from app.models import Price
from app.repositories.base.sqlalchemy_crud_repository import SQLAlchemyCrudRepository


class DummyColumn:
    def asc(self):
        return self

    def desc(self):
        return self

    def __lt__(self, other):
        return True

    def __le__(self, other):
        return True

    def __gt__(self, other):
        return True

    def __ge__(self, other):
        return True

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False


# Dummy SQLAlchemy entity base para Price
class DummyPriceBase:
    id = DummyColumn()
    seller_id = DummyColumn()
    sku = DummyColumn()
    de = DummyColumn()
    por = DummyColumn()
    created_at = DummyColumn()
    updated_at = DummyColumn()

    def __init__(self):
        self.id = None
        self.seller_id = None
        self.sku = None
        self.de = None
        self.por = None
        self.created_at = None
        self.updated_at = None


class DummyFilter:
    def to_query_dict(self):
        return {}


class DummySQLAlchemyClient:
    def get_pk_fields(self, entity_base_class):
        return ["id"]

    def to_dict(self, base):
        if base is None:
            return None
        return {
            "id": base.id,
            "seller_id": base.seller_id,
            "sku": base.sku,
            "de": base.de,
            "por": base.por,
            "created_at": base.created_at,
            "updated_at": base.updated_at,
        }

    def init_select(self, entity_base_class):
        return self

    def init_delete(self, entity_base_class):
        return self

    def where(self, condition):
        return self

    def limit(self, value):
        return self

    def offset(self, value):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def make_session(self):
        class DummySession:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                pass

            async def execute(self, stmt):
                class DummyResult:
                    def scalars(self):
                        class DummyScalars:
                            def all(inner_self):
                                return []

                        return DummyScalars()

                    def scalar_one_or_none(self):
                        return None

                    @property
                    def rowcount(self):
                        return 0

                return DummyResult()

            async def add(self, base):
                pass

            async def commit(self):
                pass

            def add(self, base):
                pass

            def begin(self):
                class DummyBegin:
                    async def __aenter__(self_):
                        return self

                    async def __aexit__(self_, exc_type, exc, tb):
                        pass

                return DummyBegin()

        return DummySession()


@pytest.fixture
def repository():
    sql_client = DummySQLAlchemyClient()
    repo = SQLAlchemyCrudRepository(sql_client=sql_client, model_class=Price, entity_base_class=DummyPriceBase)
    return repo


@pytest.mark.asyncio
async def test_to_base_and_to_model(repository):
    # Testa to_base e to_model com uma entidade Price
    entity = Price(seller_id="seller", sku="sku", de=100, por=90)
    base = repository.to_base(entity)
    assert base.seller_id == "seller"
    assert base.sku == "sku"
    assert base.de == 100
    assert base.por == 90

    base.id = 1
    model = repository.to_model(base)
    assert model.seller_id == "seller"
    assert model.sku == "sku"
    assert model.de == 100
    assert model.por == 90


@pytest.mark.asyncio
async def test_to_model_none(repository):
    # Testa to_model com base=None
    assert repository.to_model(None) is None


@pytest.mark.asyncio
async def test_create_returns_model(repository):
    # Testa se create retorna um modelo

    entity = Price(seller_id="seller", sku="sku", de=200, por=150)
    result = await repository.create(entity)
    assert isinstance(result, Price)
    assert result.seller_id == "seller"
    assert result.sku == "sku"
    assert result.de == 200
    assert result.por == 150


@pytest.mark.asyncio
async def test_apply_sort(repository):
    # Testa se _apply_sort não quebra e retorna o stmt
    class DummyStmt:
        def order_by(self, *args, **kwargs):
            return self

    stmt = DummyStmt()
    sort = {"de": 1, "por": -1, "not_a_field": 1}
    result = repository._apply_sort(stmt, sort)
    assert result is stmt


@pytest.mark.asyncio
async def test_apply_sort_with_invalid_field(repository):
    # Testa _apply_sort ignorando campo inexistente
    class DummyStmt:
        def order_by(self, *args, **kwargs):
            return self

    stmt = DummyStmt()
    sort = {"not_a_field": 1}
    result = repository._apply_sort(stmt, sort)
    assert result is stmt


@pytest.mark.asyncio
async def test_find_by_seller_id_and_sku_success(repository):
    # Monkeypatch _find_base_by_seller_id_sku_on_session para retornar base
    entity = Price(seller_id="seller", sku="sku", de=100, por=90)
    base = repository.to_base(entity)
    base.id = 1

    orig_find_base = repository._find_base_by_seller_id_sku_on_session

    async def fake_find_base(seller_id, sku, session):
        return base

    repository._find_base_by_seller_id_sku_on_session = fake_find_base

    result = await repository.find_by_seller_id_and_sku("seller", "sku")
    assert isinstance(result, Price)
    assert result.seller_id == "seller"
    assert result.sku == "sku"

    # Restaura o método original
    repository._find_base_by_seller_id_sku_on_session = orig_find_base


@pytest.mark.asyncio
async def test_find_with_sort_and_operator(repository):
    # Testa find com sort e operadores ($gt, $lt, etc)
    class Filter:
        def to_query_dict(self):
            return {"de": {"$gt": 10, "$lt": 100}, "sku": "sku"}

    results = await repository.find(Filter(), limit=5, offset=0, sort={"de": -1})
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_find_returns_empty_list(repository):
    # Testa find quando não encontra base
    results = await repository.find(DummyFilter(), limit=10, offset=0)
    assert results == []


@pytest.mark.asyncio
async def test_find_with_empty_filters(repository):
    # Testa find com filtros vazios
    class Filter:
        def to_query_dict(self):
            return {}

    results = await repository.find(Filter(), limit=5, offset=0)
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_find_by_seller_id_and_sku_returns_none(repository):
    # Testa find_by_seller_id_and_sku quando não encontra base
    result = await repository.find_by_seller_id_and_sku("seller", "sku")
    assert result is None


@pytest.mark.asyncio
async def test_update_by_seller_id_and_sku_success(repository):
    # Simula base encontrada e campos mutáveis atualizados
    entity = Price(seller_id="seller", sku="sku", de=300, por=250)
    base = repository.to_base(entity)
    base.id = 1

    # Monkeypatch o execute para retornar um DummyResult customizado
    orig_make_session = repository.sql_client.make_session

    class DummyResult:
        def scalar_one_or_none(self_):
            return base

    class PatchedSession(orig_make_session().__class__):
        async def execute(self, stmt):
            return DummyResult()

    repository.sql_client.make_session = lambda: PatchedSession()

    result = await repository.update_by_seller_id_and_sku("seller", "sku", entity)
    assert isinstance(result, Price)
    assert result.seller_id == "seller"
    assert result.sku == "sku"


@pytest.mark.asyncio
async def test_update_by_seller_id_and_sku_returns_none(repository):
    # Testa update_by_seller_id_and_sku quando não encontra base
    entity = Price(seller_id="seller", sku="sku", de=300, por=250)
    result = await repository.update_by_seller_id_and_sku("seller", "sku", entity)
    assert result is None


@pytest.mark.asyncio
async def test_update_by_seller_id_and_sku_no_base(repository):
    # Testa update_by_seller_id_and_sku quando não encontra base
    entity = Price(seller_id="seller", sku="sku", de=300, por=250)
    result = await repository.update_by_seller_id_and_sku("notfound", "sku", entity)
    assert result is None


@pytest.mark.asyncio
async def test_delete_by_seller_id_and_sku_success(repository):
    # Monkeypatch o execute para simular deleção bem-sucedida
    orig_make_session = repository.sql_client.make_session

    class DummyResult:
        @property
        def rowcount(self):
            return 1

    class PatchedSession(orig_make_session().__class__):
        async def execute(self, stmt):
            return DummyResult()

    repository.sql_client.make_session = lambda: PatchedSession()

    result = await repository.delete_by_seller_id_and_sku("seller", "sku")
    assert result is True


@pytest.mark.asyncio
async def test_delete_by_seller_id_and_sku_returns_false(repository):
    # Testa delete_by_seller_id_and_sku quando não encontra base
    result = await repository.delete_by_seller_id_and_sku("seller", "sku")
    assert result is False
