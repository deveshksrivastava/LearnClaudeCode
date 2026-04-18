# New Developer Setup Plan — ShopFast

## Context
A new developer has received this codebase on a fresh laptop and needs to get all three services running locally: the e-commerce API (port 8000), the LLM chatbot backend (port 8002), and the React frontend (port 5173). This plan covers every step from prerequisites to first successful run, including where things commonly break.

---

## Prerequisites (install first)

| Tool | Minimum Version | Why |
|------|----------------|-----|
| Git | any | clone the repo |
| Node.js | >= 18 | frontend + monorepo scripts (`package.json` engines field) |
| Python | >= 3.9 | both API backends |
| An OpenAI API key **or** Azure OpenAI credentials | — | LLM chatbot won't start without one |

---

## Step-by-Step Setup

### 1. Clone the repository
```bash
git clone <repo-url>
cd LearnClaudeCode
```

---

### 2. Install root npm dependencies
```bash
npm install
```
This installs `concurrently` (used by `npm run dev` to run all 3 services in parallel).

---

### 3. Install frontend npm dependencies
```bash
cd frontend
npm install
cd ..
```

---

### 4. Set up e-commerce API environment
```bash
# At repo root
cp .env.example .env
```
Edit `.env` and fill in **one** of:
- `OPENAI_API_KEY=sk-...`  — if using OpenAI directly
- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION` — if using Azure

The SQLite database (`ecommerce.db`) and tables are **auto-created** on first startup — no migration needed.

---

### 5. Install e-commerce API Python dependencies
```bash
# At repo root (use your system Python or a venv)
pip install -r requirements.txt
```

---

### 6. Set up LLM chatbot backend virtualenv
```bash
cd llm-chatbot-backend
python -m venv .venv          # MUST be named .venv (see Failure Points #1)
source .venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt
```

---

### 7. Set up LLM chatbot backend environment
```bash
# Inside llm-chatbot-backend/
cp .env.example .env
```
Edit `llm-chatbot-backend/.env` and set:
- `LLM_PROVIDER=openai` (or `azure`)
- `OPENAI_API_KEY=sk-...` — for OpenAI
- OR Azure equivalents: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT_NAME`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`

ChromaDB data dir (`./chroma_data`) and NLTK downloads happen **automatically** on first startup.

---

### 8. Run all three services
```bash
# From repo root
npm run dev
```
This starts all 3 services with color-coded output:
- `cyan`    → e-commerce API on http://localhost:8000
- `yellow`  → LLM chatbot on http://localhost:8002
- `magenta` → React frontend on http://localhost:5173

Or start them individually:
```bash
npm run dev:api       # e-commerce API only
npm run dev:chatbot   # LLM chatbot only
npm run dev:web       # frontend only
```

---

### 9. Verify it's working
- http://localhost:8000/docs — e-commerce API Swagger UI
- http://localhost:8002/docs — chatbot API Swagger UI
- http://localhost:5173      — React frontend

---

## Likely Failure Points

### #1 — Wrong venv name: `venv/` instead of `.venv/`
**Root cause:** `package.json` `dev:chatbot` script hardcodes `.venv/Scripts/python.exe`.
**Symptom:** `npm run dev:chatbot` fails with "No such file or directory".
**Fix:** Always create the chatbot venv as `.venv`, not `venv`.
```bash
python -m venv .venv   # correct
python -m venv venv    # WRONG — npm script won't find it
```

### #2 — Missing `.env` file
**Root cause:** `.env` is gitignored; new devs only get `.env.example`.
**Symptom:** Server fails at startup with a pydantic validation error or "STARTUP FAILED".
**Fix:** Copy both `.env.example` files and fill in API keys (steps 4 and 7).

### #3 — Wrong chromadb version on Windows
**Root cause:** `pip install chromadb` without the `>=1.0.0` pin may install 0.5.x, which requires C++ build tools.
**Symptom:** `pip install` fails with "Microsoft Visual C++ 14.0 is required".
**Fix:** The `requirements.txt` already pins `chromadb>=1.0.0`. Use it exactly — don't install chromadb manually.

### #4 — Port already in use
**Symptom:** `Address already in use` on 8000, 8002, or 5173.
**Fix:** Kill the conflicting process or change the port in the run command.

### #5 — NLTK download fails (no internet)
**Root cause:** On first run, LlamaIndex triggers NLTK to download `punkt_tab` and `stopwords` data.
**Symptom:** Startup hangs or fails with "Resource punkt_tab not found".
**Fix:** Ensure internet access on first run, or pre-download:
```python
import nltk; nltk.download('punkt_tab'); nltk.download('stopwords')
```

### #6 — Node.js version < 18
**Symptom:** npm or Vite errors about unsupported syntax.
**Fix:** Install Node.js >= 18 (use `nvm` for easy version switching).

---

## Critical Files
| File | Purpose |
|------|---------|
| `package.json` | Monorepo scripts — all `npm run dev:*` commands |
| `.env.example` | Root env template (e-commerce API + shared OpenAI keys) |
| `llm-chatbot-backend/.env.example` | Chatbot env template (LLM provider, ChromaDB, RAG settings) |
| `llm-chatbot-backend/app/config.py` | All chatbot config fields + defaults |
| `app/core/database.py` | SQLite auto-init — no manual migration needed |
| `requirements.txt` (root) | E-commerce API deps |
| `llm-chatbot-backend/requirements.txt` | Chatbot deps (includes chromadb>=1.0.0) |
