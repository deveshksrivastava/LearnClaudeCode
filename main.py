import sqlite3

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

DB_PATH = "ecommerce.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


class CartShim:
    def clear(self):
        conn = get_connection()
        conn.execute("DELETE FROM cart_items")
        conn.commit()
        conn.close()


cart = CartShim()


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    NOT NULL,
            price REAL    NOT NULL,
            stock INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            product_id INTEGER PRIMARY KEY,
            quantity   INTEGER NOT NULL
        )
    """)
    if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO products (id, name, price, stock) VALUES (?, ?, ?, ?)",
            [
                (1, "Wireless Mouse", 29.99, 50),
                (2, "Mechanical Keyboard", 89.99, 30),
                (3, "USB-C Hub", 49.99, 100),
            ],
        )
    conn.commit()
    conn.close()


init_db()


class Product(BaseModel):
    name: str
    price: float
    stock: int


class CartItem(BaseModel):
    product_id: int
    quantity: int


@app.get("/")
def root():
    return {"message": "Welcome to the ecommerce API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/products")
def get_products():
    conn = get_connection()
    rows = conn.execute("SELECT id, name, price, stock FROM products").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/products/{id}")
def get_product(id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, name, price, stock FROM products WHERE id = ?", (id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)


@app.post("/products", status_code=201)
def create_product(product: Product):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
        (product.name, product.price, product.stock),
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": new_id, "name": product.name, "price": product.price, "stock": product.stock}


@app.get("/cart")
def get_cart():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.id, p.name, p.price, p.stock, ci.quantity
        FROM cart_items ci
        JOIN products p ON p.id = ci.product_id
    """).fetchall()
    conn.close()
    items = [
        {
            "product": {"id": row["id"], "name": row["name"], "price": row["price"], "stock": row["stock"]},
            "quantity": row["quantity"],
        }
        for row in rows
    ]
    total = sum(item["product"]["price"] * item["quantity"] for item in items)
    return {"items": items, "total": round(total, 2)}


@app.post("/cart", status_code=201)
def add_to_cart(item: CartItem):
    conn = get_connection()
    product_row = conn.execute(
        "SELECT id, name, price, stock FROM products WHERE id = ?", (item.product_id,)
    ).fetchone()
    if not product_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")
    product = dict(product_row)

    existing = conn.execute(
        "SELECT quantity FROM cart_items WHERE product_id = ?", (item.product_id,)
    ).fetchone()
    current_qty = existing["quantity"] if existing else 0

    if product["stock"] < current_qty + item.quantity:
        conn.close()
        raise HTTPException(status_code=400, detail="Not enough stock")

    new_qty = current_qty + item.quantity
    if existing:
        conn.execute(
            "UPDATE cart_items SET quantity = ? WHERE product_id = ?",
            (new_qty, item.product_id),
        )
    else:
        conn.execute(
            "INSERT INTO cart_items (product_id, quantity) VALUES (?, ?)",
            (item.product_id, item.quantity),
        )
    conn.commit()
    conn.close()
    return {"product": product, "quantity": new_qty}


@app.delete("/cart/{product_id}", status_code=204)
def remove_from_cart(product_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT product_id FROM cart_items WHERE product_id = ?", (product_id,)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not in cart")
    conn.execute("DELETE FROM cart_items WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()
