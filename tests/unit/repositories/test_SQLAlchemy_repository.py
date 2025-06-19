import pytest
from app.models import Price
from app.repositories.base.sqlalchemy_crud_repository import SQLAlchemyCrudRepository


# Dummy SQLAlchemy entity base para Price
class DummyPriceBase:
    id = None
    seller_id = None
    sku = None
    de = None
    por = None
    created_at = None
    updated_at = None

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
async def test_create_returns_model(repository):
    entity = Price(seller_id="seller", sku="sku", de=200, por=150)
    result = await repository.create(entity)
    assert isinstance(result, Price)
    assert result.seller_id == "seller"
    assert result.sku == "sku"
    assert result.de == 200
    assert result.por == 150


@pytest.mark.asyncio
async def test_find_returns_empty_list(repository):
    results = await repository.find(DummyFilter(), limit=10, offset=0)
    assert results == []


@pytest.mark.asyncio
async def test_find_by_seller_id_and_sku_returns_none(repository):
    result = await repository.find_by_seller_id_and_sku("seller", "sku")
    assert result is None


@pytest.mark.asyncio
async def test_update_by_seller_id_and_sku_returns_none(repository):
    entity = Price(seller_id="seller", sku="sku", de=300, por=250)
    result = await repository.update_by_seller_id_and_sku("seller", "sku", entity)
    assert result is None


@pytest.mark.asyncio
async def test_patch_by_seller_id_and_sku_returns_none(repository):
    entity = Price(seller_id="seller", sku="sku", de=400, por=350)
    result = await repository.patch_by_seller_id_and_sku("seller", "sku", entity)
    assert result is None


@pytest.mark.asyncio
async def test_delete_by_seller_id_and_sku_returns_false(repository):
    result = await repository.delete_by_seller_id_and_sku("seller", "sku")
    assert result is False
