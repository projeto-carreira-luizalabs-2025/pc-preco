import pytest
from datetime import datetime, timedelta, timezone
from app.models.base import AuditModel

# app/models/test_base.py


def test_auditmodel_default_created_at():
    model = AuditModel()
    assert isinstance(model.created_at, datetime)
    assert model.updated_at is None
    assert model.created_by is None
    assert model.updated_by is None
    assert model.audit_created_at is None
    assert model.audit_updated_at is None


def test_auditmodel_all_fields():
    now = datetime.now(tz=timezone.utc)
    model = AuditModel(
        created_at=now,
        updated_at=now + timedelta(hours=1),
        created_by="user1",
        updated_by="user2",
        audit_created_at=now,
        audit_updated_at=now + timedelta(hours=2),
    )
    assert model.created_at == now
    assert model.updated_at == now + timedelta(hours=1)
    assert model.created_by == "user1"
    assert model.updated_by == "user2"
    assert model.audit_created_at == now
    assert model.audit_updated_at == now + timedelta(hours=2)


def test_auditmodel_accepts_none():
    model = AuditModel(
        created_at=None, updated_at=None, created_by=None, updated_by=None, audit_created_at=None, audit_updated_at=None
    )
    assert model.created_at is None
    assert model.updated_at is None
    assert model.created_by is None
    assert model.updated_by is None
    assert model.audit_created_at is None
    assert model.audit_updated_at is None


def test_auditmodel_datetime_fields():
    now = datetime.now(tz=timezone.utc)
    model = AuditModel(created_at=now, updated_at=now)
    assert isinstance(model.created_at, datetime)
    assert isinstance(model.updated_at, datetime)
