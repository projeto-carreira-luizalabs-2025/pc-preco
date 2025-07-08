import pytest
from datetime import datetime, timedelta, timezone
from app.models.base import AuditModel, UserModel

# app/models/test_base.py


def test_auditmodel_default_created_at():
    model = AuditModel()
    assert isinstance(model.created_at, datetime)
    assert model.updated_at is None
    assert model.created_by is None
    assert model.updated_by is None


def test_auditmodel_all_fields():
    now = datetime.now(tz=timezone.utc)
    model = AuditModel(
        created_at=now,
        updated_at=now + timedelta(hours=1),
        created_by=UserModel(name="user1", server="issuer1"),
        updated_by=UserModel(name="user2", server="issuer2"),
    )
    assert model.created_at == now
    assert model.updated_at == now + timedelta(hours=1)
    assert model.created_by.name == "user1"
    assert model.updated_by.name == "user2"


def test_auditmodel_accepts_none():
    model = AuditModel(
        created_at=None, updated_at=None, created_by=None, updated_by=None, audit_created_at=None, audit_updated_at=None
    )
    assert model.created_at is None
    assert model.updated_at is None
    assert model.created_by is None
    assert model.updated_by is None


def test_auditmodel_datetime_fields():
    now = datetime.now(tz=timezone.utc)
    model = AuditModel(created_at=now, updated_at=now)
    assert isinstance(model.created_at, datetime)
    assert isinstance(model.updated_at, datetime)
