import importlib


def test_redis_client_uses_environment_values(monkeypatch):
    monkeypatch.setenv("REDIS_HOST", "cache.local")
    monkeypatch.setenv("REDIS_PORT", "6380")
    monkeypatch.setenv("REDIS_PASSWORD", "secret")

    from src.store_service.extensions import redis_client as redis_module

    captured = {}

    class FakeRedis:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(redis_module.redis, "Redis", FakeRedis)
    importlib.reload(redis_module)

    assert captured["host"] == "cache.local"
    assert captured["port"] == 6380
    assert captured["password"] == "secret"
    assert captured["decode_responses"] is True
