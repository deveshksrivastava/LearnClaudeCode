# ShopFast Backend Tutorial

A beginner-friendly walkthrough of both backends — starting simple, building up.

---

## The Big Picture

The project has **two separate backends** running at the same time:

| Backend | Port | What it does |
|---------|------|--------------|
| E-commerce API | 8000 | Products, cart, users, basic AI chat |
| LLM Chatbot API | 8002 | Smart chatbot with document search |

Both are built with **FastAPI** — a Python tool for making APIs (a way for the frontend to talk to the backend).

---

## Part 1: The E-Commerce API (`app/`)

### Think of it like a supermarket

- **Frontend (React)** = the customer walking around the shop
- **Backend (FastAPI)** = the staff working behind the counter
- **Database (SQLite)** = the stockroom where everything is stored

---

### How the shop opens — `app/main.py`

```python
async def lifespan(app):
    init_db()   # Set up the stockroom before opening
    yield       # Shop is now OPEN for customers
```

When you run the server it does 2 things:
1. Creates the database tables (like setting up shelves in the stockroom)
2. Opens 4 "counters" — products, cart, users, and chat

---

### The 4 counters (routers)

#### Counter 1: Products — `app/routers/products.py`

The product shelf. Customers can:

| URL | What it does |
|-----|--------------|
| `GET /products` | Show me everything on the shelf |
| `GET /products/search?q=shoe` | Find all items with "shoe" in the name |
| `GET /products/5` | Tell me about item number 5 |
| `POST /products` | Add a new item to the shelf |

Under the hood, every request runs a SQL query:

```python
rows = conn.execute("SELECT id, name, price, stock FROM products").fetchall()
```

Translation: "Go to the stockroom, open the products table, bring everything back."

---

#### Counter 2: Cart — `app/routers/cart.py`

The shopping trolley. Key behaviours:

- **Stock check before adding** — if you want 5 bottles but only 3 are left, it returns an error
- **Adds up the total automatically** — `price × quantity` for every item in the trolley
- **Handles duplicates** — adding the same product twice increases the quantity instead of creating two rows

```python
total = sum(item["product"]["price"] * item["quantity"] for item in items)
```

---

#### Counter 3: Users — `app/routers/users.py`

The membership desk. Lets you register, update your profile, and delete your account.

Passwords are **hashed** before storing:
> SHA-256 turns your password into a scrambled string. Even if someone reads the database directly, they can't figure out your real password.

---

#### Counter 4: Chat — `app/routers/chat.py`

A basic AI shopping assistant. Before calling the AI, it fetches the full product list and injects it into the prompt:

```
System: "Here are our products: [laptop £599, shoes £49...]
         Now answer the customer's question."
User: "Do you have anything under £50?"
```

This way the AI actually knows what's in stock.

---

### How a request flows (e-commerce)

```
Browser                 FastAPI                   SQLite
  │                       │                          │
  │── GET /products ──────►│                          │
  │                       │── SELECT * FROM products ►│
  │                       │◄──────── rows ────────────│
  │◄── JSON response ─────│
```

Every endpoint: receive request → query database → return JSON.

---

## Part 2: The LLM Chatbot Backend (`llm-chatbot-backend/`)

### Same idea, but much smarter

Think of this as upgrading from a supermarket counter to a **personal shopping assistant with a library and a brain**.

---

### The "brain warm-up" — `llm-chatbot-backend/app/main.py`

When this server starts, it does **6 steps** before accepting any message:

```
Step 1: Connect to ChromaDB         ← Open the library filing cabinet
Step 2: Check for new files         ← See if any new documents were added
Step 3: Build a search index        ← Create an index of all the documents
Step 4: Connect to the LLM          ← Wake up the AI brain
Step 5: Load tools                  ← Give the AI a phone to call the shop
Step 6: Build the LangGraph graph   ← Set up the conversation assembly line
```

If any step fails, the whole server refuses to start — so you always know exactly what went wrong.

---

### Settings — `app/config.py`

All configuration lives in one place. Values come from a `.env` file:

```
OPENAI_API_KEY=sk-...
RAG_CHUNK_SIZE=256        # How big each document chunk is
RAG_TOP_K=10              # How many chunks to retrieve per query
```

Nothing is hardcoded into the logic files — if you need to change a value, you change the `.env` file, not the code.

---

### The 5-step assembly line — `app/graph/nodes.py`

Every message you send goes through 5 stations like a factory line:

```
Your message: "tell me about A Magical Day for Year 10"
      │
      ▼
Station 1: receive_input
   → Is the message empty? No → continue

      │
      ▼
Station 2: retrieve_context
   → Search ChromaDB for relevant chunks
   → "Found 3 chunks from nova.txt"

      │
      ▼
Station 3: build_prompt
   → Assemble the full message to send to the AI:
     [System: You are a helpful assistant]
     [Context: ...relevant chunks from nova.txt...]
     [Chat history: previous messages]
     [User: tell me about A Magical Day...]

      │
      ▼
Station 4: call_llm
   → Send to Azure OpenAI, get response back
   → May also trigger "tool calls" (e.g. search the shop)

      │
      ▼
Station 5: format_response
   → Clean up the reply, save this turn to conversation history

      │
      ▼
   Reply sent back to you
```

---

### The library system (RAG)

**RAG** stands for Retrieval-Augmented Generation. Here's what it means in plain English:

#### What is RAG?

> **Step 1 — Upload:** You upload a file → it gets chopped into small chunks (256 tokens each) → each chunk is converted into a vector (a list of numbers representing its meaning) → stored in ChromaDB.
>
> **Step 2 — Search:** When you ask a question → your question also becomes a vector.
>
> **Step 3 — Answer:** ChromaDB finds the chunks whose vectors are most similar to your question's vector → those chunks are sent to the AI as "context" → the AI answers using that context.

**Analogy:** Imagine highlighting the most relevant pages in a textbook before handing it to someone to answer a question. RAG does this automatically.

---

#### The document loader — `app/rag/document_loader.py`

Responsible for reading files and storing them in ChromaDB:

```
File on disk (nova.txt)
      │
      ▼
SentenceSplitter chops it into chunks (256 tokens each, 50 token overlap)
      │
      ▼
OpenAI Embeddings converts each chunk into a vector
      │
      ▼
ChromaDB stores the vector + original text + filename metadata
```

The **overlap** (50 tokens) means consecutive chunks share some content — so information at the boundary between two chunks doesn't get lost.

---

#### The retriever — `app/rag/retriever.py`

When you ask a question:

```
Query: "A Magical Day for Year 10"
      │
      ▼
Convert query to a vector (same embedding model as indexing)
      │
      ▼
ChromaDB: find top 10 most similar vectors
      │
      ▼
Return those chunks as plain text:
  [Source 1: nova.txt (similarity: 0.87)]
  A Magical Day for Year 10 — 11/12/2025
  66 students in Year 10 enjoyed a tour of Harry Potter Studios...
```

This text then gets injected into the LLM prompt at Station 3.

---

### The upload endpoint — `app/api/chat_router.py`

When you upload a file via the UI:

```
1. Validate extension (.txt, .pdf, .md only)
2. Check file size (max 10 MB)
3. Save to data/sample_docs/
4. Index into ChromaDB via load_single_file()
5. Rebuild the live search index
6. Return: filename + number of chunks created
```

After uploading, the chatbot can immediately answer questions about that file.

---

### How a chat request flows (LLM chatbot)

```
Browser                LangGraph              ChromaDB         Azure OpenAI
  │                       │                      │                  │
  │── POST /chat-llm ─────►│                      │                  │
  │                       │── vector search ─────►│                  │
  │                       │◄── top 10 chunks ─────│                  │
  │                       │── build prompt ───────────────────────── │
  │                       │◄── AI response ──────────────────────────│
  │◄── JSON response ─────│
```

---

## Part 3: Side-by-side comparison

| | E-commerce API (`app/`) | LLM Chatbot (`llm-chatbot-backend/`) |
|---|---|---|
| **Port** | 8000 | 8002 |
| **Database** | SQLite (rows & columns) | ChromaDB (vectors / meaning) |
| **How it "knows" things** | Reads from a table | Searches uploaded documents |
| **AI** | Simple one-shot prompt | 5-step pipeline with memory |
| **Startup** | Instant | ~5-10 seconds (loads indexes) |
| **Purpose** | Products, cart, users | Document-aware smart assistant |
| **Main file** | `app/main.py` | `llm-chatbot-backend/app/main.py` |
| **Key config** | `app/core/config.py` | `llm-chatbot-backend/app/config.py` |

---

## Quick reference: Key files

### E-commerce API
| File | What it does |
|------|--------------|
| `app/main.py` | App startup, database init, router registration |
| `app/core/database.py` | Creates SQLite tables |
| `app/routers/products.py` | Browse, search, add products |
| `app/routers/cart.py` | Add/remove items, calculate total |
| `app/routers/users.py` | Register, update, delete accounts |
| `app/routers/chat.py` | AI shopping assistant |
| `app/models/product.py` | Defines what a product looks like (name, price, stock) |

### LLM Chatbot
| File | What it does |
|------|--------------|
| `llm-chatbot-backend/app/main.py` | 6-step startup sequence |
| `llm-chatbot-backend/app/config.py` | All settings in one place |
| `llm-chatbot-backend/app/models.py` | Request/response data shapes |
| `llm-chatbot-backend/app/api/chat_router.py` | Chat, upload, and index endpoints |
| `llm-chatbot-backend/app/graph/nodes.py` | 5-step conversation pipeline |
| `llm-chatbot-backend/app/rag/document_loader.py` | Chop files into chunks, store in ChromaDB |
| `llm-chatbot-backend/app/rag/retriever.py` | Find relevant chunks for a query |
| `llm-chatbot-backend/app/llm/llm_provider.py` | Connect to OpenAI or Azure OpenAI |
