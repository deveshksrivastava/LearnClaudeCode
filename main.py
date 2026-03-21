from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Product(BaseModel):
    name: str
    price: float
    stock: int


class CartItem(BaseModel):
    product_id: int
    quantity: int


cart = {}  # product_id -> {"product": ..., "quantity": ...}


products = [
    {"id": 1, "name": "Wireless Mouse", "price": 29.99, "stock": 50},
    {"id": 2, "name": "Mechanical Keyboard", "price": 89.99, "stock": 30},
    {"id": 3, "name": "USB-C Hub", "price": 49.99, "stock": 100},
]


@app.get("/")
def root():
    return {"message": "Welcome to the ecommerce API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/products")
def get_products():
    return products


@app.get("/products/{id}")
def get_product(id: int):
    product = next((p for p in products if p["id"] == id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products", status_code=201)
def create_product(product: Product):
    new_id = max(p["id"] for p in products) + 1 if products else 1
    new_product = {"id": new_id, **product.model_dump()}
    products.append(new_product)
    return new_product


@app.get("/cart")
def get_cart():
    items = [
        {"product": v["product"], "quantity": v["quantity"]}
        for v in cart.values()
    ]
    total = sum(v["product"]["price"] * v["quantity"] for v in cart.values())
    return {"items": items, "total": round(total, 2)}


@app.post("/cart", status_code=201)
def add_to_cart(item: CartItem):
    product = next((p for p in products if p["id"] == item.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    current_qty = cart[item.product_id]["quantity"] if item.product_id in cart else 0
    if product["stock"] < current_qty + item.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")
    if item.product_id in cart:
        cart[item.product_id]["quantity"] += item.quantity
    else:
        cart[item.product_id] = {"product": product, "quantity": item.quantity}
    return cart[item.product_id]


@app.delete("/cart/{product_id}", status_code=204)
def remove_from_cart(product_id: int):
    if product_id not in cart:
        raise HTTPException(status_code=404, detail="Product not in cart")
    del cart[product_id]
