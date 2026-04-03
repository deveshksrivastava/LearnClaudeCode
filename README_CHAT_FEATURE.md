# ShopFast — Chat Feature Documentation

A RAG-powered (Retrieval-Augmented Generation) AI shopping assistant built with FastAPI (SSE streaming) on the backend and React + TypeScript on the frontend.

---

## Overview

The chat feature lets users ask natural-language questions about the store's products. The AI assistant responds with live-streamed answers grounded in the actual product catalog fetched from the database at request time.

```
User types message
    → POST /chat  (with session_id)
        → Fetch live product catalog from SQLite  (RAG context)
        → Fetch last 20 conversation turns from SQLite  (memory)
        → Call OpenAI / Azure OpenAI with streaming
            → Tokens streamed back via SSE  (Server-Sent Events)
                → Frontend renders tokens token-by-token
        → Full assistant reply saved to SQLite
```

---

## Architecture

### Backend (`main.py`)

#### Database Table

```sql
CREATE TABLE chat_messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT    NOT NULL,
    role       TEXT    NOT NULL,   -- 'user' or 'assistant'
    content    TEXT    NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Each chat turn (both user and assistant) is persisted against a `session_id` UUID so conversation history survives page refreshes.

---

#### AI Client Factory — `get_ai_client()`

Resolves the correct async OpenAI client from environment variables at call time:

| Priority | Condition | Client returned |
|----------|-----------|-----------------|
| 1st | `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY` both set | `AsyncAzureOpenAI` |
| 2nd | `OPENAI_API_KEY` set | `AsyncOpenAI` |
| fallback | Neither set | `None` → HTTP 503 |

```python
def get_ai_client():
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key  = os.getenv("AZURE_OPENAI_API_KEY")
    if azure_endpoint and azure_api_key:
        return AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        )
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        return AsyncOpenAI(api_key=openai_api_key)
    return None
```

The deployment/model name defaults to `gpt-4o-mini` and is overridden via `AZURE_OPENAI_DEPLOYMENT`.

---

#### API Endpoints

##### `POST /chat/session`
Creates and returns a new UUID session ID. The frontend calls this once on page load and caches the ID in `sessionStorage`.

**Response:**
```json
{ "session_id": "550e8400-e29b-41d4-a716-446655440000" }
```

---

##### `POST /chat`
The main inference endpoint.

**Request body (`ChatRequest`):**
```json
{
  "message": "What keyboards do you have?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**What happens internally:**
1. Validates that an AI client is configured (503 if not).
2. Generates a new `session_id` if one was not provided.
3. **RAG step** — queries the `products` table and injects a formatted catalog into the system prompt:
   ```
   - Wireless Mouse: $29.99, 50 in stock (ID: 1)
   - Mechanical Keyboard: $89.99, 30 in stock (ID: 2)
   - USB-C Hub: $49.99, 100 in stock (ID: 3)
   ```
4. **Memory step** — fetches the last 20 messages for the session (to stay within token budget) and prepends them to the message array.
5. Builds the full message array: `system` → `history` → `user`.
6. Persists the new user turn to `chat_messages`.
7. Calls `ai_client.chat.completions.create(..., stream=True)` and returns a `StreamingResponse`.

**Streaming response format (Server-Sent Events):**

Each line is a JSON payload prefixed with `data: `.

| Event type | Payload example |
|------------|-----------------|
| Token chunk | `data: {"token": "Sure"}` |
| AI error | `data: {"error": "Rate limit exceeded"}` |
| Stream complete | `data: {"done": true, "session_id": "..."}` |

After the stream is fully consumed, the complete assistant reply is saved to `chat_messages`.

**Response headers:**
```
Content-Type: text/event-stream
Cache-Control: no-cache
X-Accel-Buffering: no
```

---

##### `GET /chat/history/{session_id}`
Returns all messages for a session in chronological order.

**Response:**
```json
[
  { "role": "user",      "content": "What keyboards do you have?", "created_at": "2026-04-03 10:00:00" },
  { "role": "assistant", "content": "We have the Mechanical Keyboard for $89.99...", "created_at": "2026-04-03 10:00:01" }
]
```

---

##### `DELETE /chat/history/{session_id}`
Wipes all messages for the session. Returns `204 No Content`. Called when the user clicks "New conversation".

---

### Frontend

#### `src/api/chat.ts` — API Layer

| Function | Description |
|----------|-------------|
| `newChatSession()` | `POST /chat/session` → returns `session_id` string |
| `getChatHistory(sessionId)` | `GET /chat/history/{id}` → `ChatMessage[]` |
| `clearChatHistory(sessionId)` | `DELETE /chat/history/{id}` |
| `streamChat(message, sessionId, onToken, onDone, onError)` | `POST /chat` then reads the SSE stream via `ReadableStream` |

`streamChat` uses the native Fetch API `ReadableStream` to read SSE chunks. It decodes bytes via `TextDecoder`, buffers partial lines, and dispatches:
- `onToken(token)` — called for every streamed word/chunk
- `onDone(finalSessionId)` — called when `done: true` is received
- `onError(message)` — called on HTTP errors or AI errors

#### `src/pages/ChatPage.tsx` — UI Component

| State | Purpose |
|-------|---------|
| `messages` | Array of `{ role, content }` shown in the chat window |
| `input` | Controlled textarea value |
| `sessionId` | Current UUID, synced to `sessionStorage` |
| `streaming` | `true` while waiting for tokens; disables the send button and input |
| `error` | Inline error message |

**Key behaviours:**
- On mount, the page restores a session from `sessionStorage` or creates a fresh one via `POST /chat/session`.
- When `send()` is called, a placeholder assistant message `{ content: '' }` is appended immediately, then each `onToken` callback appends characters to it — creating a live typewriter effect.
- Pressing **Enter** (without Shift) submits the message.
- "New conversation" button calls `DELETE /chat/history/{id}`, removes `sessionStorage`, creates a new session, and resets `messages`.
- A CSS `.chat-cursor` span is appended to the last assistant bubble while streaming.

---

## Environment Variables

Create a `.env` file in the project root:

```env
# Option A — Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini      # optional, defaults to gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-01      # optional

# Option B — OpenAI directly
OPENAI_API_KEY=sk-...
```

Only one set of credentials is needed. Azure takes priority if both are set.

---

## Data Flow Diagram

```
┌─────────────────────────────────┐
│         ChatPage (React)        │
│                                 │
│  sessionStorage: session_id ────┼──► POST /chat/session (on first load)
│                                 │
│  send() ────────────────────────┼──► POST /chat
│                                 │        │
│  onToken → append to last msg   │◄── SSE stream (tokens)
│  onDone  → update session_id    │◄── data: {"done": true}
│  onError → show error banner    │◄── data: {"error": "..."}
│                                 │
│  handleClear() ─────────────────┼──► DELETE /chat/history/{id}
│                                 │    POST  /chat/session
└─────────────────────────────────┘

┌─────────────────────────────────┐
│         FastAPI Backend         │
│                                 │
│  POST /chat                     │
│    ├── SELECT products (RAG)    │
│    ├── SELECT last 20 msgs      │
│    ├── INSERT user turn         │
│    ├── stream_response()        │
│    │     ├── OpenAI SSE stream  │
│    │     ├── yield tokens       │
│    │     └── INSERT asst turn   │
│    └── return StreamingResponse │
└─────────────────────────────────┘
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Server-Sent Events (SSE) over WebSockets | Simpler — HTTP, no upgrade handshake, works through most proxies |
| RAG via live DB query per request | Always reflects current stock/prices without a vector store |
| Last 20 turns as context window | Balances memory vs. token cost; configurable by changing the `LIMIT` |
| Token-by-token streaming | Better perceived performance; user sees the answer forming in real time |
| `session_id` generated server-side | Guarantees UUID quality; client just stores and replays it |
| Both OpenAI and Azure OpenAI supported | Works in any environment without code changes |
