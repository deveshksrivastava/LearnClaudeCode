from fastapi import APIRouter, HTTPException

from app.core.database import get_connection
from app.models.product import Product

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
def get_products():
    conn = get_connection()
    rows = conn.execute("SELECT id, name, price, stock FROM products").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.get("/search")
def search_products(q: str = ""):
    conn = get_connection()
    escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    rows = conn.execute(
        "SELECT id, name, price, stock FROM products WHERE name LIKE ? ESCAPE '\\'",
        (f"%{escaped}%",),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.get("/{id}")
def get_product(id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, name, price, stock FROM products WHERE id = ?", (id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)


@router.post("", status_code=201)
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
