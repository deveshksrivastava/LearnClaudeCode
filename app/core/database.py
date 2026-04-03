import sqlite3

from app.core.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


class CartShim:
    """Utility used by tests to reset cart state between test runs."""

    def clear(self) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM cart_items")
        conn.commit()
        conn.close()


cart = CartShim()


def init_db() -> None:
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
