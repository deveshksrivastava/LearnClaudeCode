from fastapi import APIRouter, HTTPException

from app.core.database import get_connection
from app.models.cart import CartItem

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("")
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
            "product": {
                "id": row["id"],
                "name": row["name"],
                "price": row["price"],
                "stock": row["stock"],
            },
            "quantity": row["quantity"],
        }
        for row in rows
    ]
    total = sum(item["product"]["price"] * item["quantity"] for item in items)
    return {"items": items, "total": round(total, 2)}


@router.post("", status_code=201)
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


@router.delete("/{product_id}", status_code=204)
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
