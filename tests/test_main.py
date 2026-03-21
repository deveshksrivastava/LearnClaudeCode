import pytest
from fastapi.testclient import TestClient
from main import app, cart

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_cart():
    cart.clear()
    yield
    cart.clear()


def test_root_returns_welcome_message():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "welcome" in response.json()["message"].lower()


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_products_returns_list():
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert isinstance(products, list)
    assert len(products) >= 1


def test_post_cart_adds_product():
    response = client.post("/cart", json={"product_id": 1, "quantity": 2})
    assert response.status_code == 201
    data = response.json()
    assert data["product"]["id"] == 1
    assert data["quantity"] == 2


def test_get_cart_returns_items_and_total():
    client.post("/cart", json={"product_id": 1, "quantity": 1})
    response = client.get("/cart")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1
    assert data["total"] > 0
