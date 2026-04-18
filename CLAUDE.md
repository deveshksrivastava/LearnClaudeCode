# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**ShopFast** — Full-stack e-commerce app with an AI chatbot. Three services run concurrently:

| Service | Port | Stack |
|---------|------|-------|
| E-commerce API | 8000 | Python, FastAPI, SQLite, Uvicorn |
| LLM Chatbot API | 8002 | Python, FastAPI, LangChain, LangGraph, LlamaIndex, ChromaDB, Azure OpenAI |
| Frontend | 5173 | React, TypeScript, Vite |

## Project Structure

```
/                          # Root — e-commerce API + monorepo scripts
  app/                     # E-commerce FastAPI app
    main.py                # App factory (CORS, lifespan, router registration)
    core/
      config.py            # Settings / env vars
      database.py          # SQLite init
    models/                # Pydantic models: product, user, cart, chat
    routers/               # Route handlers: products, users, cart, chat
    services/
      ai.py                # OpenAI-backed chat service
  frontend/                # React/Vite SPA
    src/
      pages/               # LoginPage, RegisterPage, DashboardPage, ProductsPage,
                           # CartPage, ChatbotPage, LLMChatPage, UsersPage,
                           # ProjectDetailPage, FixLayout
      components/          # NavBar, ProductCard, CartItem, SearchBar
      api/                 # Typed API client wrappers
      hooks/               # Custom React hooks
      types/               # Shared TypeScript types
  llm-chatbot-backend/     # LangChain/LangGraph chatbot service
    app/
      main.py              # FastAPI app factory
      config.py            # Azure OpenAI / env config via pydantic-settings
      models.py            # Shared Pydantic models
      api/                 # Chat API routes
      graph/               # LangGraph nodes and state graph
      llm/                 # LLM client setup (Azure OpenAI)
      rag/                 # LlamaIndex + ChromaDB retrieval pipeline
    tests/                 # pytest suite: chat API, config, graph nodes, RAG retriever
  tests/                   # Root-level pytest suite for e-commerce API
  main.py                  # Legacy entrypoint (kept for reference)
```

## Commands

```bash
# ── Start everything (all 3 services in parallel) ──────────────────────────
npm run dev

# ── Individual services ────────────────────────────────────────────────────
npm run dev:api          # E-commerce API on :8000
npm run dev:chatbot      # LLM chatbot on :8002
npm run dev:web          # React frontend on :5173

# ── Install root-level JS deps ─────────────────────────────────────────────
npm install

# ── E-commerce API: Python deps ────────────────────────────────────────────
pip install -r requirements.txt
# or with uv:
uv sync

# ── LLM chatbot: Python deps (in its own venv) ─────────────────────────────
cd llm-chatbot-backend
python3 -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt

# ── Run tests ──────────────────────────────────────────────────────────────
pytest                                          # Root e-commerce tests
cd llm-chatbot-backend && pytest               # Chatbot tests

# ── Run a single test ──────────────────────────────────────────────────────
pytest tests/test_main.py::test_name -v
```

## Notes

- The LLM chatbot backend runs in its own virtualenv at `llm-chatbot-backend/.venv/`. Start it with `.venv/Scripts/python.exe -m uvicorn` (Windows).
- ChromaDB: use `chromadb>=1.0.0` — the 0.5.x series requires C++ build tools on Windows; 1.0.0+ ships pre-built wheels.
- Azure OpenAI credentials go in `llm-chatbot-backend/.env` (see `app/config.py` for required keys).
