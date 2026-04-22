# CLAUDE.md

Guidance for Claude Code when working in this repository.
Keep changes minimal and aligned with the conventions below.

## Project

**ShopFast** — full-stack e-commerce demo with an AI chatbot. Three services run concurrently in development.

| Service | Port | Path | Stack |
|---|---|---|---|
| E-commerce API | 8000 | `app/` | Python, FastAPI, SQLite, Uvicorn |
| LLM Chatbot API | 8002 | `llm-chatbot-backend/` | Python, FastAPI, LangChain, LangGraph, LlamaIndex, ChromaDB, Azure OpenAI |
| Frontend | 5173 | `frontend/` | React, TypeScript, Vite |

**Architectural boundary (important):** The chatbot service is independent. It must **not** import from the e-commerce API's `app/` package or read its SQLite DB directly. Cross-service communication is HTTP only.

## Project Structure

```
/                          # Root — e-commerce API + monorepo scripts
  app/                     # E-commerce FastAPI app
    main.py                # App factory (CORS, lifespan, router registration)
    core/
    models/                # Pydantic models: product, user, cart, chat
    routers/               # Route handlers: products, users, cart, chat
    services/
  frontend/                # React/Vite SPA
    src/{pages,components,api,hooks,types}
  llm-chatbot-backend/     # LangChain/LangGraph chatbot service
    app/{main,config,models}.py
    app/{api,graph,llm,rag}/
    tests/                 # pytest suite: chat API, config, graph nodes, RAG retriever
  tests/                  # E-commerce API pytest suite
  main.py                 # LEGACY — do not modify or extend
```
## Commands

```bash
# Run everything (3 services in parallel)
npm run dev

# Individual services
npm run dev:api         # E-commerce API :8000
npm run dev:chatbot     # LLM chatbot   :8002
npm run dev:web         # Frontend      :5173

# Dependencies
cd llm-chatbot-backend
npm install                              # Root JS deps, uv sync
python3 -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt          # E-commerce API (or: uv sync)
cd llm-chatbot-backend && pip install -r requirements.txt

# Tests
pytest                                   # E-commerce suite
cd llm-chatbot-backend && pytest         # Chatbot suite
pytest tests/test_main.py::test_name -v  # Single test
```

## Environments and secrets

- E-commerce API: `.env` at repo root. See `app/core/config.py` for keys.
- Chatbot: `llm-chatbot-backend/.env`. See `app/config.py` for required Azure OpenAI keys (deployment name, endpoint, API version, key).
- **Never commit `.env` files or real credentials.** Use placeholder values in examples.
- Azure deployment names are environment-specific — read them from config, never hardcode.

## Conventions

### Python (both services)
- Python 3.11+. Type hints on all public functions.
- FastAPI routes: one router per resource, injected dependencies for DB/session.
- Async by default for I/O (routes, DB, HTTP, LLM calls). Do not mix sync `requests` with async handlers — use `httpx.AsyncClient`.
- Pydantic v2 syntax (`model_config`, `Field`, `field_validator`). No v1 patterns.
- Imports: stdlib → third-party → local, separated by blank lines.

### TypeScript / React
- Functional components with hooks. No class components.
- Typed API client wrappers live in `frontend/src/api/` — do not call `fetch` directly from components.
- Shared types in `frontend/src/types/`. Keep DTOs in sync with Pydantic models.

### Testing
- `pytest` + `pytest-asyncio` for async code.
- Chatbot tests mock Azure OpenAI and ChromaDB — never hit real services in unit tests.
- Fixtures in `conftest.py` at the suite root. Do not duplicate fixtures per file.
- New features require tests alongside them.

## Guardrails (do not modify without explicit instruction)

- `main.py` at repo root — legacy entrypoint, kept for reference only.
- Database migration files (if present under `app/core/` or `migrations/`).
- `llm-chatbot-backend/chroma_db/` — persisted vector store, do not edit files directly.
- Generated or vendored files: `frontend/dist/`, `**/__pycache__/`, `.venv/`, `node_modules/`.

## Platform and version notes

- LLM chatbot venv path on Windows: `llm-chatbot-backend/.venv/Scripts/python.exe`. On macOS/Linux: `.venv/bin/python`.
- Use `chromadb>=1.0.0`. The 0.5.x series needs C++ build tools on Windows; 1.0.0+ ships pre-built wheels.
- SQLite is fine for dev. Any production path should assume Postgres — keep queries portable.

## When in doubt

- Prefer small, reversible changes. Show the diff before applying broad refactors.
- If a task touches the service boundary (e.g., chatbot reading e-commerce data), stop and confirm the approach first.
- If conventions here conflict with existing code in the repo, flag the inconsistency rather than silently picking one.