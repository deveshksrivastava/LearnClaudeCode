import json
import os
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.database import get_connection
from app.models.chat import ChatRequest
from app.services.ai import get_ai_client

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/session")
def new_chat_session():
    print("Creating new chat session")
    return {"session_id": str(uuid.uuid4())}


@router.post("")
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

    # RAG: inject live product catalog into the system prompt
    products = conn.execute("SELECT id, name, price, stock FROM products").fetchall()
    product_lines = "\n".join(
        f"- {p['name']}: ${p['price']:.2f}, {p['stock']} in stock (ID: {p['id']})"
        for p in products
    )

    # Conversation memory: last 20 turns to stay within token budget
    history = conn.execute(
        "SELECT role, content FROM chat_messages "
        "WHERE session_id = ? ORDER BY id DESC LIMIT 20",
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

    # Persist the user turn before streaming
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

        # Persist the completed assistant reply
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


@router.get("/history/{session_id}")
def get_chat_history(session_id: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, content, created_at FROM chat_messages "
        "WHERE session_id = ? ORDER BY id",
        (session_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.delete("/history/{session_id}", status_code=204)
def clear_chat_history(session_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
