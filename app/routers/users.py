import hashlib

from fastapi import APIRouter, HTTPException

from app.core.database import get_connection
from app.models.user import UserRegister, UserUpdate

router = APIRouter(tags=["users"])


@router.post("/register", status_code=201)
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


@router.get("/users")
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


@router.put("/users/{user_id}")
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


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    conn = get_connection()
    row = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
