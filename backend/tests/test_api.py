from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.config import allowed_origins, cookie_samesite, cookie_secure, session_secret
from app.services.auth import create_session, database_backend, get_user_for_session, revoke_session
from app.services.quality_gate import _load_model

client = TestClient(app)
buffer = BytesIO()
Image.new("RGB", (128, 128), "white").save(buffer, format="PNG")
PNG = buffer.getvalue()


def files():
    return [
        ("front", ("front.png", PNG, "image/png")),
        ("left", ("left.png", PNG, "image/png")),
        ("right", ("right.png", PNG, "image/png")),
    ]


def test_health():
    health = client.get("/api/health").json()
    assert health["status"] == "ok"
    assert health["service"] == "aerm-ai-api"
    assert health["demo_mode"] is True
    assert health["model"] == "phase1-deterministic-skin-simulator"


def test_sqlite_is_default_when_database_url_is_unset(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("AERM_DATABASE_PATH", str(tmp_path / "auth.sqlite3"))
    assert database_backend() == "sqlite"
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/aerm")
    assert database_backend() == "postgresql"


def test_auth_register_login_me_and_logout(monkeypatch, tmp_path):
    monkeypatch.setenv("AERM_DATABASE_PATH", str(tmp_path / "auth.sqlite3"))
    csrf = client.get("/api/auth/csrf").json()["csrf_token"]
    register = client.post(
        "/api/auth/register",
        json={"name": "Aarish", "email": "Aarish@example.com", "password": "secure-pass-123"},
        headers={"X-CSRF-Token": csrf},
    )
    assert register.status_code == 201
    assert register.json()["email"] == "aarish@example.com"
    assert "aerm_session" in register.cookies
    rotated_csrf = client.cookies.get("aerm_csrf")
    assert rotated_csrf and rotated_csrf != csrf

    duplicate = client.post(
        "/api/auth/register",
        json={"name": "Other", "email": "aarish@example.com", "password": "secure-pass-123"},
        headers={"X-CSRF-Token": rotated_csrf},
    )
    assert duplicate.status_code == 409

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["name"] == "Aarish"

    logged_out = client.post("/api/auth/logout", headers={"X-CSRF-Token": rotated_csrf})
    assert logged_out.status_code == 204
    assert client.get("/api/auth/me").status_code == 401

    login_csrf = client.get("/api/auth/csrf").json()["csrf_token"]
    login = client.post(
        "/api/auth/login",
        json={"email": "AARISH@example.com", "password": "secure-pass-123"},
        headers={"X-CSRF-Token": login_csrf},
    )
    assert login.status_code == 200
    login_rotated_csrf = client.cookies.get("aerm_csrf")
    assert login_rotated_csrf and login_rotated_csrf != login_csrf
    assert client.get("/api/auth/me").status_code == 200

    bad_login = client.post(
        "/api/auth/login",
        json={"email": "aarish@example.com", "password": "wrong-pass"},
        headers={"X-CSRF-Token": client.cookies.get("aerm_csrf")},
    )
    assert bad_login.status_code == 401
    assert client.post("/api/auth/logout", headers={"X-CSRF-Token": login_rotated_csrf}).status_code == 204
    relogin_csrf = client.get("/api/auth/csrf").json()["csrf_token"]
    relogin = client.post(
        "/api/auth/login",
        json={"email": "aarish@example.com", "password": "secure-pass-123"},
        headers={"X-CSRF-Token": relogin_csrf},
    )
    assert relogin.status_code == 200
    assert client.post(
        "/api/auth/logout",
        headers={"X-CSRF-Token": client.cookies.get("aerm_csrf")},
    ).status_code == 204


def test_logout_requires_csrf_token(monkeypatch, tmp_path):
    monkeypatch.setenv("AERM_DATABASE_PATH", str(tmp_path / "auth.sqlite3"))
    csrf = client.get("/api/auth/csrf").json()["csrf_token"]
    register = client.post(
        "/api/auth/register",
        json={"name": "CSRF User", "email": "csrf@example.com", "password": "secure-pass-123"},
        headers={"X-CSRF-Token": csrf},
    )
    assert register.status_code == 201
    assert client.post("/api/auth/logout").status_code == 403
    token = client.cookies.get("aerm_csrf")
    assert client.post("/api/auth/logout", headers={"X-CSRF-Token": "wrong"}).status_code == 403
    assert client.post("/api/auth/logout", headers={"X-CSRF-Token": token}).status_code == 204


@pytest.mark.parametrize("path,payload", [
    ("/api/auth/register", {"name": "Missing", "email": "missing@example.com", "password": "secure-pass-123"}),
    ("/api/auth/login", {"email": "missing@example.com", "password": "secure-pass-123"}),
])
def test_auth_mutations_require_matching_csrf(path, payload, monkeypatch, tmp_path):
    monkeypatch.setenv("AERM_DATABASE_PATH", str(tmp_path / "auth.sqlite3"))
    client.get("/api/auth/csrf")
    assert client.post(path, json=payload).status_code == 403
    assert client.post(path, json=payload, headers={"X-CSRF-Token": "wrong"}).status_code == 403


def test_security_configuration(monkeypatch, tmp_path):
    monkeypatch.setenv("AERM_ENV", "production")
    monkeypatch.delenv("AERM_SESSION_SECRET", raising=False)
    session_secret.cache_clear()
    with pytest.raises(RuntimeError, match="AERM_SESSION_SECRET"):
        session_secret()

    monkeypatch.setenv("AERM_SESSION_SECRET", "x" * 32)
    monkeypatch.delenv("AERM_COOKIE_SECURE", raising=False)
    with pytest.raises(RuntimeError, match="AERM_COOKIE_SECURE"):
        cookie_secure()
    monkeypatch.setenv("AERM_COOKIE_SECURE", "true")
    monkeypatch.setenv("AERM_COOKIE_SAMESITE", "invalid")
    with pytest.raises(RuntimeError, match="AERM_COOKIE_SAMESITE"):
        cookie_samesite()
    monkeypatch.setenv("AERM_COOKIE_SAMESITE", "none")
    assert cookie_secure() is True
    monkeypatch.delenv("AERM_ALLOWED_ORIGINS", raising=False)
    with pytest.raises(RuntimeError, match="AERM_ALLOWED_ORIGINS"):
        allowed_origins()
    monkeypatch.setenv("AERM_ALLOWED_ORIGINS", "*")
    with pytest.raises(RuntimeError, match="cannot contain"):
        allowed_origins()
    monkeypatch.setenv("AERM_ALLOWED_ORIGINS", "https://app.example.com")
    assert allowed_origins() == ["https://app.example.com"]
    secure_csrf = client.get("/api/auth/csrf")
    assert "Secure" in secure_csrf.headers["set-cookie"]
    monkeypatch.setenv("AERM_ENV", "development")
    monkeypatch.delenv("AERM_COOKIE_SAMESITE", raising=False)
    monkeypatch.delenv("AERM_COOKIE_SECURE", raising=False)
    session_secret.cache_clear()


def test_session_token_revocation(monkeypatch, tmp_path):
    monkeypatch.setenv("AERM_DATABASE_PATH", str(tmp_path / "auth.sqlite3"))
    csrf = client.get("/api/auth/csrf").json()["csrf_token"]
    register = client.post(
        "/api/auth/register",
        json={"name": "Session User", "email": "session@example.com", "password": "secure-pass-123"},
        headers={"X-CSRF-Token": csrf},
    )
    assert register.status_code == 201
    token = register.cookies.get("aerm_session")
    assert token
    assert get_user_for_session(token)
    revoke_session(token)
    assert get_user_for_session(token) is None


def test_analyze_requires_all_views():
    response = client.post("/api/analyze", files=[files()[0]])
    assert response.status_code == 422


def test_analyze_is_deterministic_and_labelled():
    first = client.post("/api/analyze", files=files(), data={"budget_inr": "850", "fragrance_free": "true"})
    second = client.post("/api/analyze", files=files(), data={"budget_inr": "850", "fragrance_free": "true"})
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert "Simulated Phase 1" in first.json()["simulation_notice"]
    assert first.json()["views"] == ["front", "left", "right"]
    assert first.json()["routine"]
    assert first.json()["matched_ingredients"]
    assert all(product["price_inr"] <= 850 for product in first.json()["products"])
    assert first.json()["image_quality"] is None


def test_analyze_includes_optional_quality_gate(monkeypatch, tmp_path):
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC
    from ml.quality_baseline import extract_features_from_bytes
    import pickle
    import numpy as np

    bright = PNG
    dark_buffer = BytesIO()
    Image.new("RGB", (128, 128), "black").save(dark_buffer, format="PNG")
    dark = dark_buffer.getvalue()
    model = Pipeline(
        [("scale", StandardScaler()), ("classifier", SVC(kernel="rbf", probability=False))]
    )
    model.fit(
        np.vstack([extract_features_from_bytes(bright), extract_features_from_bytes(dark)]),
        np.array([1, 0]),
    )
    checkpoint = tmp_path / "quality.pkl"
    with checkpoint.open("wb") as handle:
        pickle.dump(model, handle)
    monkeypatch.setenv("AERM_QUALITY_MODEL_PATH", str(checkpoint))
    _load_model.cache_clear()

    response = client.post("/api/analyze", files=files())
    assert response.status_code == 200
    quality = response.json()["image_quality"]
    assert quality["available"] is True
    assert quality["model"].startswith("SCIN RBF SVM")
    assert [item["view"] for item in quality["views"]] == ["front", "left", "right"]
    assert all(item["score_kind"] == "decision_score" for item in quality["views"])
    monkeypatch.delenv("AERM_QUALITY_MODEL_PATH")
    _load_model.cache_clear()


def test_analyze_reports_invalid_quality_checkpoint(monkeypatch):
    monkeypatch.setenv("AERM_QUALITY_MODEL_PATH", "C:\\missing\\quality.pkl")
    _load_model.cache_clear()
    response = client.post("/api/analyze", files=files())
    assert response.status_code == 503
    assert "missing checkpoint" in response.json()["detail"]
    monkeypatch.delenv("AERM_QUALITY_MODEL_PATH")
    _load_model.cache_clear()


def test_quality_checkpoint_digest_is_verified(monkeypatch, tmp_path):
    checkpoint = tmp_path / "quality.pkl"
    checkpoint.write_bytes(b"not-a-model")
    monkeypatch.setenv("AERM_QUALITY_MODEL_SHA256", "0" * 64)
    _load_model.cache_clear()
    with pytest.raises(ValueError, match="SHA256"):
        _load_model(str(checkpoint))
    monkeypatch.delenv("AERM_QUALITY_MODEL_SHA256")
    _load_model.cache_clear()


def test_analyze_rejects_non_images():
    bad = [("front", ("front.txt", b"not an image", "text/plain")), *files()[1:]]
    assert client.post("/api/analyze", files=bad).status_code == 415


def test_analyze_rejects_tiny_or_undecodable_images():
    tiny = BytesIO()
    Image.new("RGB", (32, 32), "white").save(tiny, format="PNG")
    tiny_files = [("front", ("front.png", tiny.getvalue(), "image/png")), *files()[1:]]
    assert client.post("/api/analyze", files=tiny_files).status_code == 422
    corrupt = [("front", ("front.png", b"\x89PNG\r\n\x1a\nnot-real", "image/png")), *files()[1:]]
    assert client.post("/api/analyze", files=corrupt).status_code == 422


def test_products_and_ingredient_matching():
    products = client.get("/api/products")
    assert products.status_code == 200
    assert {"price_inr", "brand", "sample_data", "source", "fragrance_free", "availability"} <= products.json()[0].keys()
    response = client.post("/api/recommendations", json={"concerns": ["acne"], "budget_inr": 900, "fragrance_free": True, "preferred_ingredients": ["azelaic acid"]})
    assert response.status_code == 200
    assert any("azelaic acid" in product["ingredients"] for product in response.json()["products"])
    assert response.json()["routine"]
    assert response.json()["matched_ingredients"]
    assert response.json()["explanations"]


def test_catalogue_filters_and_sorting():
    response = client.get("/api/products", params={"category": "serum", "max_budget": 800, "ingredient": "niacinamide", "sort": "price_asc"})
    assert response.status_code == 200
    products = response.json()
    assert products
    assert all(product["category"] == "serum" for product in products)
    assert all(product["price_inr"] <= 800 for product in products)
    assert all(any("niacinamide" in ingredient.lower() for ingredient in product["ingredients"]) for product in products)
    assert [product["price_inr"] for product in products] == sorted(product["price_inr"] for product in products)
