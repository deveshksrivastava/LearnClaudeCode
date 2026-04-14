  
## LLM Chatbot Backend — Architecture Overview                                                                               
  llm-chatbot-backend/ — a production-grade FastAPI chatbot with RAG support.                                               

  ---
##  Tech Stack
```
  ┌───────────────────────┬───────────────────────────────────────────────────┐
  │         Layer         │                    Technology                     │
  ├───────────────────────┼───────────────────────────────────────────────────┤
  │ API Framework         │ FastAPI + Uvicorn                                 │
  ├───────────────────────┼───────────────────────────────────────────────────┤
  │ LLM                   │ OpenAI / Azure OpenAI (switchable)                │
  ├───────────────────────┼───────────────────────────────────────────────────┤
  │ Conversation Pipeline │ Custom sequential pipeline (originally LangGraph) │
  ├───────────────────────┼───────────────────────────────────────────────────┤
  │ RAG Retrieval         │ LlamaIndex (VectorStoreIndex)                     │
  ├───────────────────────┼───────────────────────────────────────────────────┤
  │ Vector Store          │ ChromaDB (persistent, on-disk)                    │
  ├───────────────────────┼───────────────────────────────────────────────────┤
  │ Config                │ pydantic-settings (reads .env)                    │
  └───────────────────────┴───────────────────────────────────────────────────┘
```
  ---
###    Folder Structure
```
  app/
  ├── main.py              # App entry point, startup lifecycle
  ├── config.py            # All settings from .env
  ├── models.py            # Pydantic request/response schemas
  ├── api/
  │   ├── chat_router.py   # POST /api/v1/chat-llm, POST /api/v1/index
  │   └── health_router.py # GET /api/v1/health
  ├── graph/
  │   ├── graph_builder.py # Assembles the pipeline
  │   ├── nodes.py         # 5 pipeline node functions
  │   └── state.py         # ConversationState TypedDict
  ├── llm/
  │   ├── llm_provider.py  # Returns ChatOpenAI or AzureChatOpenAI
  │   └── prompt_templates.py  # RAG prompt + simple chat prompt
  └── rag/
      ├── document_loader.py  # Reads .txt/.pdf, chunks, embeds, stores in ChromaDB
      ├── retriever.py        # Queries ChromaDB and returns relevant chunks
      └── vector_store.py     # ChromaDB client + LlamaIndex index builder
```
  ---
###    Startup Sequence (main.py)

  When the server starts, it does this in order:

  1. ChromaDB — connects to the persistent vector store
  2. Auto-index — scans data/sample_docs/, indexes any new .txt/.pdf files not yet in ChromaDB
  3. LlamaIndex — builds a VectorStoreIndex on top of ChromaDB (for semantic search)
  4. LLM — creates a LangChain ChatOpenAI or AzureChatOpenAI client
  5. Pipeline — builds the ConversationPipeline and stores everything on app.state

  ---
###  Conversation Pipeline (5 Nodes)

  Each request to POST /api/v1/chat-llm runs through these nodes in sequence:

  receive_input → retrieve_context → build_prompt → call_llm → format_response
```
  ┌──────────────────┬───────────────────────────────────────────────────────────────────────────────────┐
  │       Node       │                                   What it does                                    │
  ├──────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ receive_input    │ Validates the user's message is not empty                                         │
  ├──────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ retrieve_context │ Embeds the query, searches ChromaDB for top-k relevant chunks                     │
  ├──────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ build_prompt     │ Picks RAG template (with context) or simple template (no docs), adds chat history │
  ├──────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ call_llm         │ Calls llm.invoke() with the formatted prompt                                      │
  ├──────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
  │ format_response  │ Extracts text from AIMessage, appends to session history, returns final answer    │
  └──────────────────┴───────────────────────────────────────────────────────────────────────────────────┘
```
  Each node is a factory function (closure) that captures dependencies like the LLM or index, then returns a plain (state:
  dict) -> dict function.

  ---
  ### API Endpoints
```
  ┌────────┬──────────────────┬─────────────────────────────────────────────────────┐
  │ Method │       Path       │                     Description                     │
  ├────────┼──────────────────┼─────────────────────────────────────────────────────┤
  │ GET    │ /api/v1/health   │ Health check (used by Azure load balancer)          │
  ├────────┼──────────────────┼─────────────────────────────────────────────────────┤
  │ POST   │ /api/v1/chat-llm │ Send a message; requires session_id + message       │
  ├────────┼──────────────────┼─────────────────────────────────────────────────────┤
  │ POST   │ /api/v1/index    │ Load .txt/.pdf files from a directory into ChromaDB │
  ├────────┼──────────────────┼─────────────────────────────────────────────────────┤
  │ GET    │ /docs            │ Swagger UI (auto-generated)                         │
  └────────┴──────────────────┴─────────────────────────────────────────────────────┘
```
  ---
 ###   Session Memory

  - Conversation history is stored in-memory in a dict: _session_store[session_id] → list[messages]
  - Same session_id = same conversation thread (multi-turn)
  - For production: replace with Redis / Azure Cache for Redis

  ---
  ###  LLM Provider (Switchable)

  Set LLM_PROVIDER=openai or LLM_PROVIDER=azure in .env. The llm_provider.py module returns the appropriate LangChain
  client. Azure requires AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_NAME.

  ---
  ###  RAG Flow

  1. Documents from data/sample_docs/ are chunked (512 tokens, 50 overlap)
  2. Each chunk is embedded via OpenAI Embeddings and stored in ChromaDB
  3. On each chat request, the user's query is embedded and the top-6 most similar chunks are retrieved
  4. Those chunks are injected into the LLM prompt as [Source N: filename (similarity: 0.xx)]
  5. The response includes a sources list so the frontend can show citations

  
  # llm-chatbot-backend — Complete                                                                                  
                                                                                                                  
  43/43 tests pass | Server starts and responds | All quality gates pass                                          
     
  ### What was built                                                                                                  
  ```                                                                                                              
  llm-chatbot-backend/
  ├── app/
  │   ├── main.py              ← FastAPI app + lifespan startup
  │   ├── config.py            ← pydantic-settings (all config from .env)
  │   ├── models.py            ← Pydantic request/response schemas
  │   ├── graph/               ← LangGraph: state.py, nodes.py, graph_builder.py
  │   ├── rag/                 ← vector_store.py, document_loader.py, retriever.py
  │   ├── llm/                 ← llm_provider.py, prompt_templates.py
  │   └── api/                 ← chat_router.py, health_router.py
  ├── tests/                   ← 43 pytest tests (all passing)
  ├── docs/llm-start.md        ← Full educational guide (10 sections + glossary)
  ├── infra/                   ← Azure Bicep IaC
  ├── Dockerfile, docker-compose.yml, azure.yaml, README.md
  └── .env.example, requirements.txt, pytest.ini
```
  ### To run the backend
  ```
  cd llm-chatbot-backend
  cp .env.example .env

  Edit .env: set OPENAI_API_KEY=sk-your-real-key
  ```

  ### Install deps
  pip install -r requirements.txt

  ### Start server
  ```
  uvicorn app.main:app --reload
  → http://localhost:8000/docs (Swagger UI)
  → curl http://localhost:8000/api/v1/health
  ```
  #### Index docs, then chat
  ```
  curl -X POST http://localhost:8000/api/v1/index -H "Content-Type: application/json" -d '{"directory":
  "./data/sample_docs"}'
  curl -X POST http://localhost:8000/api/v1/chat-llm -H "Content-Type: application/json" -d '{"session_id": "s1",
  "message": "What is the return policy?"}'
  ```
  
  # Run tests
  .venv/Scripts/python.exe -m pytest tests/ -v

  ### Key notes

  - ChromaDB: Uses >=1.0.0 (0.5.x requires C++ build tools on Windows — not available)
  - LangGraph flow: receive_input → retrieve_context → build_prompt → call_llm → format_response → END
  - Multi-turn memory: Stored in-memory by session_id (replace with Redis for production)
  - Azure deployment: azd auth login && azd env set OPENAI_API_KEY "..." && azd up

### ✻ Crunched for 31m 0s                       
                                                                                
- ● Background command "cd D:/sites/LearnClaudeCode/llm-chatbot-backend &amp;&amp; .venv/Scripts/python.exe -m pip  
install "chromadb&gt;=1.0.0" --prefer-binary 2&gt;&amp;1 | tail -10" completed (exit code 0)                      
                                                                                                                  
- ● The background task completed successfully — that was the initial chromadb installation that finished after we'd
   already moved on. No action needed.                                                                            

