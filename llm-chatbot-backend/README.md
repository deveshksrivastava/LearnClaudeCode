# LLM Chatbot Backend

A production-grade, Azure-deployable chatbot backend built with **FastAPI**, **LangChain**, **LangGraph**, **LlamaIndex**, and **ChromaDB**.

## Features

- Multi-turn conversation memory (LangGraph state)
- RAG (Retrieval-Augmented Generation) with ChromaDB
- OpenAI and Azure OpenAI support
- REST API (FastAPI)
- Docker + Azure Container Apps deployment

## Quick Start

```bash
cp .env.example .env
# Edit .env: add your OPENAI_API_KEY

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API explorer.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/chat` | Send a chat message |
| `POST` | `/api/v1/index` | Index documents into ChromaDB |

### Example: Chat

```bash
# First, index the sample documents
curl -X POST http://localhost:8000/api/v1/index \
  -H "Content-Type: application/json" \
  -d '{"directory": "./data/sample_docs"}'

# Then chat
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user-1", "message": "What is the return policy?"}'
```

## Project Structure

```
llm-chatbot-backend/
├── app/
│   ├── main.py              ← FastAPI app + lifespan startup
│   ├── config.py            ← All settings (pydantic-settings)
│   ├── models.py            ← Request/response schemas
│   ├── graph/               ← LangGraph nodes and graph assembly
│   ├── rag/                 ← ChromaDB + LlamaIndex RAG pipeline
│   ├── llm/                 ← LLM client and prompt templates
│   └── api/                 ← FastAPI routers
├── data/sample_docs/        ← Drop .txt/.pdf files here to index
├── tests/                   ← Pytest test suite
├── docs/llm-start.md        ← Full educational guide
├── infra/                   ← Azure Bicep IaC
├── Dockerfile
├── docker-compose.yml
└── azure.yaml               ← Azure Developer CLI config
```

## Docker Compose (Local Development)

```bash
docker-compose up --build
```

Starts both the FastAPI server (port 8000) and ChromaDB (port 8001).

## Run Tests

```bash
pytest tests/ -v
```

## Azure Deployment

```bash
azd auth login
azd env set OPENAI_API_KEY "sk-..."
azd up
```

See [docs/llm-start.md](docs/llm-start.md) for the complete step-by-step guide including educational explanations of every concept.

## Architecture

```
User → FastAPI → LangGraph Graph → [receive_input → retrieve_context → build_prompt → call_llm → format_response] → Response
                                         ↕
                                    ChromaDB (via LlamaIndex)
                                         ↕
                                    OpenAI Embeddings API
```

## Configuration

All configuration is in `.env` (copy from `.env.example`). Key variables:

| Variable | Description |
|---|---|
| `LLM_PROVIDER` | `openai` or `azure` |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `LLM_TEMPERATURE` | 0.0–2.0, controls creativity |
| `CHROMA_PERSIST_PATH` | Where ChromaDB stores data |
| `RAG_TOP_K` | Number of chunks to retrieve per query |
