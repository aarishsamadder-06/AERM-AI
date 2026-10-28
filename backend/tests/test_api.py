from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

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
