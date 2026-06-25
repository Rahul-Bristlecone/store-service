import inspect

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from store_service.resources import store as store_resource


def _unwrap(method):
    return inspect.unwrap(method)


class _QueryFirst:
    def __init__(self, value):
        self.value = value

    def filter_by(self, **_kwargs):
        return self

    def first(self):
        return self.value


class _QueryAll:
    def __init__(self, values):
        self.values = values

    def filter_by(self, **_kwargs):
        return self

    def all(self):
        return self.values


class _QueryGetOr404:
    def __init__(self, value):
        self.value = value

    def get_or_404(self, _store_id):
        return self.value


def test_validate_active_session_rejects_invalid_json(monkeypatch):
    from flask import Flask

    app = Flask(__name__)
    monkeypatch.setattr(store_resource.redis_client, "get", lambda _key: "not-json")

    with app.test_request_context(headers={"Authorization": "Bearer token"}):
        with pytest.raises(Exception) as exc_info:
            store_resource.validate_active_session(user_id=5)

    assert getattr(exc_info.value, "code", None) == 401


def test_validate_active_session_rejects_token_mismatch(monkeypatch):
    from flask import Flask

    app = Flask(__name__)
    monkeypatch.setattr(store_resource.redis_client, "get", lambda _key: '{"token":"other-token"}')

    with app.test_request_context(headers={"Authorization": "Bearer token"}):
        with pytest.raises(Exception) as exc_info:
            store_resource.validate_active_session(user_id=5)

    assert getattr(exc_info.value, "code", None) == 401


def test_store_get_returns_query_result(monkeypatch):
    expected_store = object()
    fake_model = type("FakeStoreModel", (), {"query": _QueryGetOr404(expected_store)})
    monkeypatch.setattr(store_resource, "StoreModel", fake_model)

    result = _unwrap(store_resource.Store.get)(store_resource.Store(), "11")

    assert result is expected_store


def test_store_delete_success(monkeypatch):
    calls = {}
    fake_store = object()

    monkeypatch.setattr(store_resource, "get_jwt_identity", lambda: "42")
    monkeypatch.setattr(store_resource, "validate_active_session", lambda _user_id: None)
    monkeypatch.setattr(store_resource, "get_user_product_or_404", lambda _store_id, _user_id: fake_store)
    monkeypatch.setattr(store_resource.db.session, "delete", lambda store: calls.setdefault("deleted", store))
    monkeypatch.setattr(store_resource.db.session, "commit", lambda: calls.setdefault("committed", True))

    result = _unwrap(store_resource.Store.delete)(store_resource.Store(), "77")

    assert result == {"message": "store deleted with store id 77"}
    assert calls["deleted"] is fake_store
    assert calls["committed"] is True


def test_store_put_rejects_product_code(monkeypatch):
    monkeypatch.setattr(store_resource, "get_jwt_identity", lambda: "42")
    monkeypatch.setattr(store_resource, "validate_active_session", lambda _user_id: None)
    monkeypatch.setattr(store_resource, "get_user_product_or_404", lambda _store_id, _user_id: object())

    with pytest.raises(Exception) as exc_info:
        _unwrap(store_resource.Store.put)(
            store_resource.Store(),
            {"product_code": "x"},
            "8",
        )

    assert getattr(exc_info.value, "code", None) == 400


def test_store_put_success_updates_store(monkeypatch):
    class _Store:
        user_id = 1
        store_id = 9
        store_name = "old"

    calls = {}
    store = _Store()

    monkeypatch.setattr(store_resource, "get_jwt_identity", lambda: "42")
    monkeypatch.setattr(store_resource, "validate_active_session", lambda _user_id: None)
    monkeypatch.setattr(store_resource, "get_user_product_or_404", lambda _store_id, _user_id: store)
    monkeypatch.setattr(store_resource.db.session, "add", lambda value: calls.setdefault("added", value))
    monkeypatch.setattr(store_resource.db.session, "commit", lambda: calls.setdefault("committed", True))

    result = _unwrap(store_resource.Store.put)(
        store_resource.Store(),
        {"store_name": "new-name", "user_id": 99, "store_id": 100},
        "9",
    )

    assert result is store
    assert store.store_name == "new-name"
    assert store.user_id == 1
    assert store.store_id == 9
    assert calls["added"] is store
    assert calls["committed"] is True


def test_store_put_handles_integrity_error(monkeypatch):
    class _Store:
        pass

    monkeypatch.setattr(store_resource, "get_jwt_identity", lambda: "42")
    monkeypatch.setattr(store_resource, "validate_active_session", lambda _user_id: None)
    monkeypatch.setattr(store_resource, "get_user_product_or_404", lambda _store_id, _user_id: _Store())
    monkeypatch.setattr(store_resource.db.session, "add", lambda _value: None)
    monkeypatch.setattr(
        store_resource.db.session,
        "commit",
        lambda: (_ for _ in ()).throw(IntegrityError("stmt", "params", Exception("dup"))),
    )
    rollback_calls = {"count": 0}
    monkeypatch.setattr(
        store_resource.db.session,
        "rollback",
        lambda: rollback_calls.__setitem__("count", rollback_calls["count"] + 1),
    )

    with pytest.raises(Exception) as exc_info:
        _unwrap(store_resource.Store.put)(store_resource.Store(), {"store_name": "x"}, "9")

    assert getattr(exc_info.value, "code", None) == 400
    assert rollback_calls["count"] == 1


def test_store_put_handles_sqlalchemy_error(monkeypatch):
    class _Store:
        pass

    monkeypatch.setattr(store_resource, "get_jwt_identity", lambda: "42")
    monkeypatch.setattr(store_resource, "validate_active_session", lambda _user_id: None)
    monkeypatch.setattr(store_resource, "get_user_product_or_404", lambda _store_id, _user_id: _Store())
    monkeypatch.setattr(store_resource.db.session, "add", lambda _value: None)
    monkeypatch.setattr(
        store_resource.db.session,
        "commit",
        lambda: (_ for _ in ()).throw(SQLAlchemyError("db error")),
    )
    rollback_calls = {"count": 0}
    monkeypatch.setattr(
        store_resource.db.session,
        "rollback",
        lambda: rollback_calls.__setitem__("count", rollback_calls["count"] + 1),
    )

    with pytest.raises(Exception) as exc_info:
        _unwrap(store_resource.Store.put)(store_resource.Store(), {"store_name": "x"}, "9")

    assert getattr(exc_info.value, "code", None) == 500
    assert rollback_calls["count"] == 1


def test_store_list_get_filters_by_user(monkeypatch):
    expected = [object(), object()]
    fake_model = type("FakeStoreModel", (), {"query": _QueryAll(expected)})
    monkeypatch.setattr(store_resource, "StoreModel", fake_model)
    monkeypatch.setattr(store_resource, "get_jwt_identity", lambda: "12")

    result = _unwrap(store_resource.StoreList.get)(store_resource.StoreList())

    assert result == expected


def test_store_create_post_success(monkeypatch):
    calls = {"execute": 0}
    expected_store = object()
    fake_model = type("FakeStoreModel", (), {"query": _QueryFirst(expected_store)})

    monkeypatch.setattr(store_resource, "StoreModel", fake_model)
    monkeypatch.setattr(store_resource, "get_jwt_identity", lambda: "24")
    monkeypatch.setattr(store_resource, "validate_active_session", lambda _user_id: None)
    monkeypatch.setattr(
        store_resource.db.session,
        "execute",
        lambda _stmt, params: calls.update({"execute": calls["execute"] + 1, "params": params}),
    )
    monkeypatch.setattr(store_resource.db.session, "commit", lambda: calls.setdefault("committed", True))

    result = _unwrap(store_resource.StoreCreate.post)(
        store_resource.StoreCreate(),
        {
            "store_number": 10,
            "customer_name": "A",
            "store_name": "S",
            "address_line1": "L1",
            "address_line2": None,
            "address_line3": None,
            "pin_code": "123456",
            "state_code": "KA",
            "country_code": "IN",
            "shipping_time": 2,
        },
    )

    assert result is expected_store
    assert calls["execute"] == 1
    assert calls["params"]["user_id"] == 24
    assert calls["committed"] is True


def test_store_create_post_handles_integrity_error(monkeypatch):
    monkeypatch.setattr(store_resource, "get_jwt_identity", lambda: "24")
    monkeypatch.setattr(store_resource, "validate_active_session", lambda _user_id: None)
    monkeypatch.setattr(
        store_resource.db.session,
        "execute",
        lambda _stmt, _params: (_ for _ in ()).throw(IntegrityError("stmt", "params", Exception("dup"))),
    )
    rollback_calls = {"count": 0}
    monkeypatch.setattr(
        store_resource.db.session,
        "rollback",
        lambda: rollback_calls.__setitem__("count", rollback_calls["count"] + 1),
    )

    with pytest.raises(Exception) as exc_info:
        _unwrap(store_resource.StoreCreate.post)(
            store_resource.StoreCreate(),
            {
                "store_number": 10,
                "customer_name": "A",
                "store_name": "S",
                "address_line1": "L1",
                "address_line2": None,
                "address_line3": None,
                "pin_code": "123456",
                "state_code": "KA",
                "country_code": "IN",
                "shipping_time": 2,
            },
        )

    assert getattr(exc_info.value, "code", None) == 400
    assert rollback_calls["count"] == 1


def test_store_create_post_handles_sqlalchemy_error(monkeypatch):
    monkeypatch.setattr(store_resource, "get_jwt_identity", lambda: "24")
    monkeypatch.setattr(store_resource, "validate_active_session", lambda _user_id: None)
    monkeypatch.setattr(
        store_resource.db.session,
        "execute",
        lambda _stmt, _params: (_ for _ in ()).throw(SQLAlchemyError("db down")),
    )
    rollback_calls = {"count": 0}
    monkeypatch.setattr(
        store_resource.db.session,
        "rollback",
        lambda: rollback_calls.__setitem__("count", rollback_calls["count"] + 1),
    )

    with pytest.raises(Exception) as exc_info:
        _unwrap(store_resource.StoreCreate.post)(
            store_resource.StoreCreate(),
            {
                "store_number": 10,
                "customer_name": "A",
                "store_name": "S",
                "address_line1": "L1",
                "address_line2": None,
                "address_line3": None,
                "pin_code": "123456",
                "state_code": "KA",
                "country_code": "IN",
                "shipping_time": 2,
            },
        )

    assert getattr(exc_info.value, "code", None) == 500
    assert rollback_calls["count"] == 1
