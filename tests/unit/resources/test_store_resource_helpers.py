import pytest
from flask import Flask

from store_service.resources import store as store_resource


class _FakeQuery:
    def __init__(self, result):
        self._result = result

    def filter_by(self, **_kwargs):
        return self

    def first(self):
        return self._result


def test_validate_active_session_success(monkeypatch):
    app = Flask(__name__)

    monkeypatch.setattr(
        store_resource.redis_client,
        "get",
        lambda _key: '{"token": "valid-token"}',
    )

    with app.test_request_context(headers={"Authorization": "Bearer valid-token"}):
        store_resource.validate_active_session(user_id=10)


def test_validate_active_session_rejects_missing_authorization_header():
    app = Flask(__name__)

    with app.test_request_context(headers={}):
        with pytest.raises(Exception) as exc_info:
            store_resource.validate_active_session(user_id=10)

    assert getattr(exc_info.value, "code", None) == 401


def test_get_user_product_or_404_returns_store(monkeypatch):
    expected_store = object()
    fake_model = type(
        "FakeStoreModel",
        (),
        {"query": _FakeQuery(result=expected_store)},
    )
    monkeypatch.setattr(store_resource, "StoreModel", fake_model)

    result = store_resource.get_user_product_or_404(store_id=1, user_id=1)

    assert result is expected_store


def test_get_user_product_or_404_raises_404(monkeypatch):
    fake_model = type(
        "FakeStoreModel",
        (),
        {"query": _FakeQuery(result=None)},
    )
    monkeypatch.setattr(store_resource, "StoreModel", fake_model)

    with pytest.raises(Exception) as exc_info:
        store_resource.get_user_product_or_404(store_id=1, user_id=1)

    assert getattr(exc_info.value, "code", None) == 404
