import pytest

from app.models.query import QueryModel


class DummyQuery(QueryModel):
    price__ge: int | None = None
    price__gt: int | None = None
    price__le: int | None = None
    price__lt: int | None = None
    name: str | None = None
    category: str | None = None


def test_to_query_dict_with_comparison_operators():
    q = DummyQuery(price__ge=10, price__lt=20, name="item")
    result = q.to_query_dict()
    assert result == {"price": {"$gte": 10, "$lt": 20}, "name": "item"}


def test_to_query_dict_with_all_operators():
    q = DummyQuery(price__ge=5, price__gt=3, price__le=15, price__lt=12, category="books")
    result = q.to_query_dict()
    assert result == {"price": {"$gte": 5, "$gt": 3, "$lte": 15, "$lt": 12}, "category": "books"}


def test_to_query_dict_with_no_operators():
    q = DummyQuery(name="test", category="tools")
    result = q.to_query_dict()
    assert result == {"name": "test", "category": "tools"}


def test_to_query_dict_excludes_none_fields():
    q = DummyQuery(price__ge=None, price__lt=50, name=None, category="misc")
    result = q.to_query_dict()
    assert result == {"price": {"$lt": 50}, "category": "misc"}


def test_to_query_dict_empty():
    q = DummyQuery()
    result = q.to_query_dict()
    assert result == {}
