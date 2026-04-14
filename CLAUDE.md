# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**ShopFast** — Full-stack e-commerce app with an AI chatbot. Three services run concurrently:

| Service | Port | Stack |
|---------|------|-------|
| E-commerce API | 8000 | Python, FastAPI, SQLite, Uvicorn |
| LLM Chatbot API | 8002 | Python, FastAPI, LangChain, LangGraph, LlamaIndex, ChromaDB, Azure OpenAI |
| Frontend | 5173 | React, TypeScript, Vite |

## Goal: Maintain a clean, scalable, production-grade architecture with strict API contract alignment.
---
# Core Engineering Principles

- Prefer minimal, targeted changes over large refactors.
- Never assume API contracts — always verify from backend schemas.
- Keep frontend and backend strictly aligned.
- Preserve backward compatibility unless explicitly asked.
- Follow existing project patterns before introducing new ones.
- Avoid introducing new libraries without strong justification.

---
# Architecture Overview

Frontend:
- Located in: ./frontend
- React-based UI
- Uses centralized API client/service layer

Backend:
- Located in: ./llm-chatbot-backend
- FastAPI with Pydantic models
- Router → Service → Repository pattern (follow existing structure)

Data Flow:
UI → API Client → FastAPI Router → Service → Database

---
## Project Structure

```
/                          # Root — e-commerce API + monorepo scripts
  main.py                  # Legacy entrypoint (kept for reference)
  pyproject.toml           # Python project config
  requirements.txt         # E-commerce API dependencies
  pytest.ini               # Root pytest config
  playwright.config.ts     # Playwright e2e config
  package.json             # Monorepo npm scripts
  app/                     # E-commerce FastAPI app
    main.py                # App factory (CORS, lifespan, router registration)
    core/
      config.py            # Settings / env vars
      database.py          # SQLite init
    models/                # Pydantic models: product, user, cart, chat
    routers/               # Route handlers: products, users, cart, chat
    services/
      ai.py                # OpenAI-backed chat service
  docs/
    superpowers/
      plans/               # Feature planning docs
      specs/               # Architecture / design specs
  e2e/                     # Playwright end-to-end tests
    01-auth.spec.ts
    02-products.spec.ts
    03-llm-chat.spec.ts
    04-api-health.spec.ts
  frontend/                # React/Vite SPA
    src/
      pages/               # LoginPage, RegisterPage, DashboardPage, ProductsPage,
                           # CartPage, ChatbotPage, LLMChatPage, UsersPage,
                           # ProjectDetailPage, FixLayout
      components/          # NavBar, ProductCard, CartItem, SearchBar
      api/                 # Typed API client wrappers (auth, cart, chatbotApi,
                           # client, products, users)
      hooks/               # useCart, useProducts
      data/                # Static data (projects.ts)
      types/               # Shared TypeScript types (index.ts)
  llm-chatbot-backend/     # LangChain/LangGraph chatbot service
    app/
      main.py              # FastAPI app factory
      config.py            # Azure OpenAI / env config via pydantic-settings
      models.py            # Shared Pydantic models
      api/                 # chat_router.py, health_router.py
      graph/               # graph_builder.py, nodes.py, state.py
      llm/                 # llm_provider.py, prompt_templates.py, tools.py
      rag/                 # document_loader.py, retriever.py, vector_store.py
    chroma_data/           # Persisted ChromaDB vector store
    data/
      sample_docs/         # Source documents for RAG ingestion
    docs/                  # Chatbot-specific documentation
    infra/                 # Azure deployment Bicep templates
      container-app.bicep
      main.bicep
    tests/                 # pytest suite: chat API, config, graph nodes, RAG retriever
  tests/                   # Root-level pytest suite for e-commerce API
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
pip install -r requirements.txt

# ── Run tests ──────────────────────────────────────────────────────────────
pytest                                          # Root e-commerce tests
cd llm-chatbot-backend && pytest               # Chatbot tests

# ── Run a single test ──────────────────────────────────────────────────────
pytest tests/test_main.py::test_name -v
```
# Frontend Rules
- Keep API calls in a dedicated service/API layer.
- Do NOT call APIs directly from UI components unless already the pattern.
- Avoid duplicated state and unnecessary re-renders.
- Reuse existing hooks and components.

---
# Backend Rules

- Use Pydantic models for all request/response schemas.
- Keep routers thin; move logic to services where applicable.
- Use explicit HTTP status codes.
- Always validate inputs server-side.
- Avoid hidden side effects.
---
# Testing Rules

Before completing a task:
- Validate happy path
- Validate failure cases
- Validate permission/auth failures
- Update or mention missing tests
---
# Expected Response Format
When working on tasks:
1. Understanding
2. Impacted files
3. API contract impact
4. Implementation approach
5. Risks
6. Tests

Do not jump directly to code without analysis.
## Notes

- The LLM chatbot backend runs in its own virtualenv at `llm-chatbot-backend/.venv/`. Start it with `.venv/Scripts/python.exe -m uvicorn` (Windows).
- ChromaDB: use `chromadb>=1.0.0` — the 0.5.x series requires C++ build tools on Windows; 1.0.0+ ships pre-built wheels.
- Azure OpenAI credentials go in `llm-chatbot-backend/.env` (see `app/config.py` for required keys).
