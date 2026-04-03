import hashlib
import json
import os
import sqlite3
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import AsyncAzureOpenAI, AsyncOpenAI
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()





CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")


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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            email    TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT    NOT NULL,
            role       TEXT    NOT NULL,
            content    TEXT    NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


@app.get("/")
def root():
    return {"message": "Welcome to the ecommerce Fast API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/products")
def get_products():
    conn = get_connection()
    rows = conn.execute("SELECT id, name, price, stock FROM products").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/products/search")
def search_products(q: str = ""):
    conn = get_connection()
    escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    rows = conn.execute(
        "SELECT id, name, price, stock FROM products WHERE name LIKE ? ESCAPE '\\'",
        (f"%{escaped}%",),
    ).fetchall()
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


class UserUpdate(BaseModel):
    name: str
    email: EmailStr


@app.post("/register", status_code=201)
def register(user: UserRegister):
    hashed = hashlib.sha256(user.password.encode()).hexdigest()
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM users WHERE email = ?", (user.email,)
    ).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (user.name, user.email, hashed),
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": new_id, "name": user.name, "email": user.email}


@app.get("/users")
def list_users(q: str = ""):
    conn = get_connection()
    if q:
        escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        rows = conn.execute(
            "SELECT id, name, email FROM users WHERE name LIKE ? OR email LIKE ? ESCAPE '\\'",
            (f"%{escaped}%", f"%{escaped}%"),
        ).fetchall()
    else:
        rows = conn.execute("SELECT id, name, email FROM users").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.put("/users/{user_id}")
def update_user(user_id: int, data: UserUpdate):
    conn = get_connection()
    row = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    conflict = conn.execute(
        "SELECT id FROM users WHERE email = ? AND id != ?", (data.email, user_id)
    ).fetchone()
    if conflict:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already in use")
    conn.execute(
        "UPDATE users SET name = ?, email = ? WHERE id = ?",
        (data.name, data.email, user_id),
    )
    conn.commit()
    conn.close()
    return {"id": user_id, "name": data.name, "email": data.email}


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    conn = get_connection()
    row = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Chat (RAG shopping assistant)
# ---------------------------------------------------------------------------

def get_ai_client():
    """Return AsyncAzureOpenAI if Azure creds present, else AsyncOpenAI, else None."""
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if azure_endpoint and azure_api_key:
        return AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        )
    openai_api_key = os.getenv("OPENAI_API_KEY")

    print(f"AI client config - Azure: {bool(azure_endpoint and azure_api_key)}, OpenAI: {bool(openai_api_key)}")
    if openai_api_key:
        return AsyncOpenAI(api_key=openai_api_key)
    return None

class ChatRequest(BaseModel):
    message: str
    session_id: str = ""


@app.post("/chat/session")
def new_chat_session():
    print("Creating new chat session")
    """Create a fresh session ID the client can reuse."""
    return {"session_id": str(uuid.uuid4())}


@app.post("/chat")
async def chat(request: ChatRequest):
    print(f"Received chat message: {request.message} (session: {request.session_id})")
    ai_client = get_ai_client()
    if not ai_client:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI service not configured. "
                "Set AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY "
                "or OPENAI_API_KEY in your .env file."
            ),
        )

    session_id = request.session_id or str(uuid.uuid4())

    conn = get_connection()

    # RAG context: inject live product catalog
    products = conn.execute(
        "SELECT id, name, price, stock FROM products"
    ).fetchall()
    product_lines = "\n".join(
        f"- {p['name']}: ${p['price']:.2f}, {p['stock']} in stock (ID: {p['id']})"
        for p in products
    )

    # Conversation history (last 20 turns to stay within token budget)
    history = conn.execute(
        """SELECT role, content FROM chat_messages
           WHERE session_id = ? ORDER BY id DESC LIMIT 20""",
        (session_id,),
    ).fetchall()
    history = list(reversed(history))

    conn.close()

    system_prompt = (
        "You are a helpful shopping assistant for ShopFast, an e-commerce store.\n"
        "Help customers find products, check pricing/availability, and guide purchases.\n\n"
        f"Current product catalog:\n{product_lines}\n\n"
        "Be concise and friendly. If asked about a product not in the catalog, "
        "say it is not currently available."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages += [{"role": r["role"], "content": r["content"]} for r in history]
    messages.append({"role": "user", "content": request.message})

    # Persist the user turn
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, "user", request.message),
    )
    conn.commit()
    conn.close()

    async def stream_response():
        full_response = ""
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
        try:
            stream = await ai_client.chat.completions.create(
                model=deployment,
                messages=messages,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
            return

        # Persist assistant turn after full response is collected
        conn = get_connection()
        conn.execute(
            "INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, "assistant", full_response),
        )
        conn.commit()
        conn.close()
        yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/chat/history/{session_id}")
def get_chat_history(session_id: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, content, created_at FROM chat_messages "
        "WHERE session_id = ? ORDER BY id",
        (session_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.delete("/chat/history/{session_id}", status_code=204)
def clear_chat_history(session_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
