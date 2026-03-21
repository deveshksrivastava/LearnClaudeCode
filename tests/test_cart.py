import pytest
from fastapi.testclient import TestClient
from main import app, cart

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_cart():
    cart.clear()
    yield
    cart.clear()


# GET /cart

def test_get_cart_empty():
    response = client.get("/cart")
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0.0}


def test_get_cart_with_items():
    client.post("/cart", json={"product_id": 1, "quantity": 2})
    response = client.get("/cart")
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert data["total"] == round(29.99 * 2, 2)


# POST /cart

def test_add_to_cart():
    response = client.post("/cart", json={"product_id": 1, "quantity": 1})
    assert response.status_code == 201
    assert response.json()["quantity"] == 1
    assert response.json()["product"]["id"] == 1


def test_add_to_cart_increases_quantity():
    client.post("/cart", json={"product_id": 1, "quantity": 2})
    client.post("/cart", json={"product_id": 1, "quantity": 3})
    response = client.get("/cart")
    assert response.json()["items"][0]["quantity"] == 5


def test_add_to_cart_product_not_found():
    response = client.post("/cart", json={"product_id": 999, "quantity": 1})
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_add_to_cart_insufficient_stock():
    response = client.post("/cart", json={"product_id": 1, "quantity": 999})
    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough stock"


def test_add_to_cart_stock_accounts_for_existing_cart():
    # Product 1 has 50 stock — add 48, then try to add 3 more
    client.post("/cart", json={"product_id": 1, "quantity": 48})
    response = client.post("/cart", json={"product_id": 1, "quantity": 3})
    assert response.status_code == 400


# DELETE /cart/{product_id}

def test_remove_from_cart():
    client.post("/cart", json={"product_id": 1, "quantity": 1})
    response = client.delete("/cart/1")
    assert response.status_code == 204
    assert client.get("/cart").json()["items"] == []


def test_remove_from_cart_not_found():
    response = client.delete("/cart/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not in cart"


def test_cart_total_multiple_products():
    client.post("/cart", json={"product_id": 1, "quantity": 1})  # 29.99
    client.post("/cart", json={"product_id": 2, "quantity": 1})  # 89.99
    total = client.get("/cart").json()["total"]
    assert total == round(29.99 + 89.99, 2)
