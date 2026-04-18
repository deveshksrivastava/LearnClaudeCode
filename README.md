# ShopFast — Full-Stack E-Commerce App

A full-stack e-commerce application built with **FastAPI** (Python) on the backend and **React + TypeScript** (Vite) on the frontend.

---

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Python, FastAPI, SQLite, Uvicorn    |
| Frontend  | React 19, TypeScript, Vite, Axios   |
| Routing   | React Router v7                     |
| Styling   | Plain CSS (global stylesheet)       |

---

## Project Structure Demo

```
LearnClaudeCode/
├── main.py                  # FastAPI application (all API endpoints)
├── requirements.txt         # Python dependencies
├── pytest.ini               # Pytest configuration
├── ecommerce.db             # SQLite database (auto-generated)
├── tests/
│   ├── test_main.py         # General API tests
│   └── test_cart.py         # Cart-specific tests
└── frontend/                # React + TypeScript frontend
    ├── src/
    │   ├── api/             # Axios API service layer
    │   ├── components/      # Reusable UI components
    │   ├── hooks/           # Custom React hooks
    │   ├── pages/           # Page-level components
    │   └── types/           # Shared TypeScript interfaces
    └── vite.config.ts
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+


### Backend Setup with UV 
```
 uv --version
 uv init - this create .toml project file
 uv venv - this will create.env project
 .venv/Scripts/activate - activate enviornment
 now add file requirement.txt and update the package
 uv add -r requirements.txt
 uv add <<library-name>>
```


### Backend Setup with PIP

```bash
# Install Python dependencies
pip install fastapi uvicorn

# 1. Activate the virtual environment
source .venv/Scripts/activate        # Git Bash
# OR
.venv\Scripts\activate               # PowerShell / CMD

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. Start the server
uvicorn main:app --reload

If you get the "port already in use" error, port 8000 has a stale process. Fix it with one of these:

Option A — use a different port:
uvicorn main:app --reload --port 8080

Option B — kill whatever is on 8000 (run in PowerShell as Admin):
# Find the PID
netstat -ano | findstr :8000

# Kill it (replace 12345 with the actual PID)
Stop-Process -Id 12345 -Force

Option C — one-liner to free port 8000 (PowerShell):
Get-NetTCPConnection -LocalPort 8000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

 - API runs at: **http://127.0.0.1:8000**
 - Interactive docs: **http://127.0.0.1:8000/docs**

## Run Curls/runbackend
```
curl -s -X POST http://localhost:8002/api/v1/index -H 'Content-Type: application/json' -d '{"directory": "./data/sample_docs"}' 2>&1

cd llm-chatbot-backend/  && venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

cd llm-chatbot-backend/ && venv/Scripts/python.exe -c "from app.models import UploadResponse; print('OK')"
````

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Frontend runs at: **http://localhost:5173**

### Run Both Servers Together

```bash
# cd frontend
# npm run dev:all
npm run dev
# uvicorn app.main:app --reload
# npm run de
```

---

# Backend API

```
app/
├── __init__.py
├── main.py              ← FastAPI app factory, middleware, router registration
├── core/
│   ├── config.py        ← env var settings (DB_PATH, CHAT_DEPLOYMENT)
│   └── database.py      ← get_connection(), init_db(), CartShim
├── models/
│   ├── product.py       ← Product
│   ├── cart.py          ← CartItem
│   ├── user.py          ← UserRegister, UserUpdate
│   └── chat.py          ← ChatRequest
├── routers/
│   ├── products.py      ← GET/POST /products
│   ├── cart.py          ← GET/POST/DELETE /cart
│   ├── users.py         ← /register, /users CRUD
│   └── chat.py          ← /chat, /chat/session, /chat/history
└── services/
    └── ai.py            ← get_ai_client() (Azure / OpenAI factory)

main.py  ← thin root shim: re-exports `app` and `cart` for backward compat
```

## API Endpoints

| Method   | Endpoint                  | Description                        |
|----------|---------------------------|------------------------------------|
| `GET`    | `/`                       | Welcome message                    |
| `GET`    | `/health`                 | Health check                       |
| `GET`    | `/products`               | List all products                  |
| `GET`    | `/products/search?q=`     | Search products by name            |
| `GET`    | `/products/{id}`          | Get a single product               |
| `POST`   | `/products`               | Create a new product               |
| `GET`    | `/cart`                   | Get cart items and total           |
| `POST`   | `/cart`                   | Add item to cart                   |
| `DELETE` | `/cart/{product_id}`      | Remove item from cart              |

---

## Frontend Pages

| Route      | Page           | Description                                  |
|------------|----------------|----------------------------------------------|
| `/login`   | Login          | Stylish sign-in form with email & password   |
| `/`        | Products       | Product grid with live search (300ms debounce)|
| `/cart`    | Cart           | Cart items, line totals, and order total     |

---

## Running Tests

```bash
# Run all backend tests
pytest

# Run a specific test
pytest tests/test_main.py::test_name -v
```

---

## Default Seed Data

The database is seeded automatically on first run:

| Product             | Price   | Stock |
|---------------------|---------|-------|
| Wireless Mouse      | $29.99  | 50    |
| Mechanical Keyboard | $89.99  | 30    |
| USB-C Hub           | $49.99  | 100   |


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


## How to do testing 
```
┌─────────────────────────────┬──────────────────────────────────────────────────────────────────────────┐  
  │            File             │                               What changed                               │  
  ├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤  
  │                             │ 5 LangChain tools: search_products, list_all_products,                   │  
  │ app/llm/tools.py (new)      │ get_product_details, view_cart, add_to_cart — each calls the e-commerce  │  
  │                             │ API via httpx                                                            │  
  ├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤  
  │ app/graph/state.py          │ Added llm_response, tool_calls, tool_results fields to ConversationState │  
  ├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤  
  │                             │ make_call_llm_node now accepts tools and uses .bind_tools(); new         │  
  │ app/graph/nodes.py          │ make_execute_tools_node executes tool calls and wraps results in         │  
  │                             │ ToolMessage                                                              │  
  ├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ app/graph/graph_builder.py  │ Pipeline now branches: after call_llm, if tool_calls are present it runs │
  │                             │  execute_tools → call_llm (second pass) → format_response                │
  ├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ app/config.py               │ Added ecommerce_api_url setting (defaults to http://localhost:8000)      │
  ├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ app/main.py                 │ Initialises tools at startup with get_tools(settings.ecommerce_api_url), │
  │                             │  passes them to the pipeline                                             │
  ├─────────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
  │ app/llm/prompt_templates.py │ System prompt updated to "ShopFast Assistant" — tells the LLM it has     │
  │                             │ tools and when to use them                                               │
  └─────────────────────────────┴──────────────────────────────────────────────────────────────────────────┘
```

 ### To test it, start both services and try:
  #### Terminal 1
  `npm run dev:api       # e-commerce API on :8000`

  #### Terminal 2
  `npm run dev:chatbot   # LLM chatbot on :8002`

  #### Then in the frontend LLM Chat page (or via curl):
  - "What products do you sell?" → LLM calls list_all_products
  - "Search for headphones" → LLM calls search_products("headphones")
  - "Add product 1 to my cart" → LLM calls add_to_cart(1, 1)
  - "What's in my cart?" → LLM calls view_cart

# LangGraph in llm-chatbot-backend

## The Core Concept: State + Nodes

LangGraph's fundamental idea is **state-driven pipelines**: data flows through a series of nodes as a shared dictionary. Each node reads from it, does one job, and returns only the fields it changed.

```
User Request
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│                   ConversationState                      │
│  session_id, messages, user_input, retrieved_context,   │
│  sources, built_prompt, llm_response, tool_calls,        │
│  tool_results, final_response, error                     │
└─────────────────────────────────────────────────────────┘
     │
     ▼  receive_input    → validates user message
     ▼  retrieve_context → queries ChromaDB for docs
     ▼  build_prompt     → formats history + context into LangChain messages
     ▼  call_llm         → sends to LLM (with tools bound)
     ▼  execute_tools    → (only if LLM called a tool)
     ▼  call_llm again   → (second pass with tool results)
     ▼  format_response  → extracts text, updates message history
     │
     ▼
  API Response
```

---

## 1. The State — `app/graph/state.py`

```python
class ConversationState(TypedDict):
    session_id: str        # Which user session
    messages: list[dict]   # Full history: [{"role": "human", "content": "..."}]
    user_input: str        # Current question
    retrieved_context: str # RAG chunks from ChromaDB
    sources: list[str]     # Which docs were retrieved
    built_prompt: list     # Final LangChain message list for LLM
    llm_response: Any      # Raw AIMessage (may contain .tool_calls)
    tool_calls: list       # Tools the LLM wants to call
    tool_results: list     # Results of executing those tools
    final_response: str    # Final text sent back to user
    error: str             # Any error that occurred
```

> Think of this as the **relay baton** — every node receives the full state and adds its contribution.

---

## 2. The Nodes — `app/graph/nodes.py`

Each node is a plain function `(state) -> dict`. The factory pattern is used so nodes can receive dependencies (like the LLM or index) without global variables.

| Node | Job | Key Output |
|---|---|---|
| `make_receive_input_node` | Validates message isn't empty | `error` |
| `make_retrieve_context_node` | Queries ChromaDB for relevant docs | `retrieved_context`, `sources` |
| `make_build_prompt_node` | Formats history + context into LangChain messages | `built_prompt` |
| `make_call_llm_node(llm, tools)` | Calls LLM; detects tool call requests | `llm_response`, `tool_calls` |
| `make_execute_tools_node(tools)` | Runs requested tools, wraps in `ToolMessage` | `tool_results` |
| `make_format_response_node` | Extracts text, saves to history | `final_response`, `messages` |

### Tool Calling Hook — `nodes.py:223`

```python
llm_to_use = llm.bind_tools(tools) if tools else llm
```

`.bind_tools()` tells the LLM what functions are available. The model's response then either contains `tool_calls` (use a tool) or just `.content` (answer directly).

---

## 3. The Pipeline — `app/graph/graph_builder.py`

This project replaced LangGraph's `StateGraph` with a plain Python class that does the same thing:

```python
class ConversationPipeline:
    def invoke(self, state):
        # Run receive_input → retrieve_context → build_prompt
        for name, node_fn in self._pre_llm_nodes:
            updates = node_fn(current_state)
            current_state.update(updates)   # ← merge partial dict into state

        # First LLM call
        current_state.update(self._call_llm(current_state))

        # Tool calling branch (only if LLM requested tools)
        if current_state.get("tool_calls"):
            current_state.update(self._execute_tools(current_state))

            # Append AIMessage + ToolMessages to prompt, then call LLM again
            current_state["built_prompt"] += [llm_response] + tool_results
            current_state.update(self._call_llm(current_state))

        # Final formatting
        current_state.update(self._format_response(current_state))
        return current_state
```

> The tool branch is why there are sometimes **two LLM calls**: first to decide which tool to use, second to answer after seeing the tool results.

---

## 4. The Full Request Flow

```
POST /api/v1/chat-llm
   │
   ├─ chat_router.py retrieves compiled_graph from app.state
   ├─ run_conversation_graph() builds the initial state dict
   ├─ compiled_graph.invoke(state) runs the pipeline
   │     ├─ receive_input:    validates "What products do you sell?"
   │     ├─ retrieve_context: finds return_policy.txt from ChromaDB
   │     ├─ build_prompt:     formats into [SystemMessage, HumanMessage]
   │     ├─ call_llm:         LLM responds with tool_call: list_all_products()
   │     ├─ execute_tools:    calls GET /products → returns product list
   │     ├─ call_llm again:   LLM sees products, answers naturally
   │     └─ format_response:  saves to session history
   └─ Returns {"response": "We sell: Laptop $999, Mouse $29..."}
```

> The graph is built **once at startup** (`main.py:133-141`) with LLM + ChromaDB index + tools all wired in, then reused for every request.

---

## 5. Why LangGraph (this pattern)?

| Without LangGraph | With This Pattern |
|---|---|
| Spaghetti function passing variables around | Clean state flows through typed dict |
| Hard to add new steps | Add a new node, insert it in the list |
| Hard to test individual steps | Each node is testable in isolation |
| No conditional branching | `if tool_calls:` branch is explicit |
| No error propagation | Any node sets `error`, others skip |

---

## Further Deep-Dives

- How the tool calling two-pass flow works in detail
- How RAG retrieval connects to ChromaDB
- How to add a new node to the pipeline
- How session memory works across turns

# How to use Claude Code 

A good sequence for you is:
```
ask for implementation plan
ask for one tiny change
run locally
fix exact error
commit
push after a stable checkpoint
```

## Phase 1: Planning only
First ask for analysis, not code.
Example:
```
    Analyze this codebase change only. Do not write code yet.

    Goal: add file upload feature to frontend and backend.

    Please give:

    files that need to change
    backend changes
    frontend changes
    risks
    step-by-step implementation plan in very small tasks
    likely failure points

    Keep the plan practical and based on the existing code.
```

This forces the model to think before editing.

## Phase 2: One change at a time

Then give one bounded task.
```
    Implement only step 1.

    Task:
    Create a backend FastAPI endpoint to accept a single file upload.

    Constraints:

    * do not change frontend
    * do not refactor unrelated code
    * keep the route isolated
    * tell me exactly which files you changed
    * show how I should test it with Swagger or curl

```

## Phase 3: Test immediately

After every small change:
```
run app
run affected test
hit endpoint
inspect logs
commit if good
```
Do not wait until 10 changes are done.