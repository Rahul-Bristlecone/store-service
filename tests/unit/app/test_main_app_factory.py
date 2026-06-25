from src.store_service import main as main_module


def test_create_app_configures_extensions_and_health_route(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://a.example.com, https://b.example.com")
    monkeypatch.setenv("MYSQL_USER", "user")
    monkeypatch.setenv("MYSQL_PASSWORD", "pass")
    monkeypatch.setenv("DB_HOST", "dbhost")
    monkeypatch.setenv("DB_PORT", "3307")
    monkeypatch.setenv("MYSQL_DATABASE", "store_db")
    monkeypatch.setenv("JWT_SECRET_KEY", "secret")

    calls = {}

    def fake_cors(app, **kwargs):
        calls["cors_app"] = app
        calls["cors_kwargs"] = kwargs

    class FakeApi:
        def __init__(self, app):
            calls["api_app"] = app

        def register_blueprint(self, blueprint):
            calls["registered_blueprint"] = blueprint

    monkeypatch.setattr(main_module, "CORS", fake_cors)
    monkeypatch.setattr(main_module, "Api", FakeApi)
    monkeypatch.setattr(main_module, "JWTManager", lambda app: calls.setdefault("jwt_app", app))
    monkeypatch.setattr(main_module.db, "init_app", lambda app: calls.setdefault("db_init_app", app))
    monkeypatch.setattr(main_module.db, "create_all", lambda: calls.setdefault("db_create_all", True))

    app = main_module.create_app()

    assert app.config["SQLALCHEMY_DATABASE_URI"] == "mysql+pymysql://user:pass@dbhost:3307/store_db"
    assert calls["cors_kwargs"]["origins"] == ["https://a.example.com", "https://b.example.com"]
    assert calls["db_create_all"] is True
    assert calls["registered_blueprint"] is main_module.StoreBp

    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}
