# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This is the FastAPI application entry point — the "main" file that Uvicorn loads.
# It creates the FastAPI app, registers startup/shutdown lifecycle events,
# includes all API routers, and configures logging.
#
# STARTUP ORDER:
#   1. Load settings from .env
#   2. Initialise ChromaDB client and collection
#   3. Build LlamaIndex VectorStoreIndex (if documents exist in ChromaDB)
#   4. Initialise LLM client (OpenAI or Azure OpenAI)
#   5. Build and compile the LangGraph conversation graph
#   6. Store everything on app.state for use by API endpoints
# ─────────────────────────────────────────────────────────────────────────────

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
load_dotenv()  # Load .env into os.environ before any library (e.g. LlamaIndex) reads it

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.llm.llm_provider import get_llm
from app.llm.tools import get_tools
from app.rag.document_loader import load_documents_from_directory, SUPPORTED_EXTENSIONS
from app.rag.vector_store import get_chroma_client, get_or_create_collection, build_vector_store_index
from app.graph.graph_builder import build_conversation_graph
from app.api import chat_router, health_router


def configure_logging(log_level: str) -> None:
    """
    Configures Python's root logger to write structured logs.

    WHY CONFIGURE LOGGING HERE?
      All modules use logger = logging.getLogger(__name__).
      Configuring once at startup ensures all loggers use the same format
      and log level, making debugging much easier.

    Args:
        log_level: Logging level string (e.g., "INFO", "DEBUG", "WARNING").
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,  # Azure Container Apps reads from stdout for log ingestion
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager — handles startup and shutdown.

    WHY LIFESPAN INSTEAD OF @app.on_event?
      @app.on_event("startup") is deprecated in modern FastAPI.
      The lifespan context manager is the current best practice.
      Code before 'yield' runs at startup; code after 'yield' runs at shutdown.

    Args:
        app: The FastAPI application instance.

    Yields:
        None (FastAPI convention — the yield point is when the app is "running").
    """
    # ── STARTUP ──────────────────────────────────────────────────────────
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Starting LLM Chatbot Backend v{settings.app_version}")
    logger.info(f"LLM Provider: {settings.llm_provider}")

    try:
        # Step 1: ChromaDB — initialise the persistent vector store
        logger.info("Initialising ChromaDB...")
        chroma_client = get_chroma_client(settings)
        collection = get_or_create_collection(chroma_client, settings)
        app.state.chroma_client = chroma_client      # Store for /index endpoint
        app.state.chroma_collection = collection

        # Step 2: Auto-sync data/sample_docs — index any files not yet in ChromaDB
        # SAFE approach: never delete the collection object (keeps app.state reference valid).
        # Instead, wipe entries via collection.delete() and re-index when new files are found.
        # Use path relative to this file so it works regardless of CWD.
        docs_dir = Path(__file__).parent.parent / "data" / "sample_docs"
        if docs_dir.exists():
            disk_files = {f.name for f in docs_dir.iterdir() if f.suffix in SUPPORTED_EXTENSIONS}
            if disk_files:
                indexed_files: set = set()
                if collection.count() > 0:
                    results = collection.get(include=["metadatas"])
                    indexed_files = {
                        m.get("file_name", "")
                        for m in (results.get("metadatas") or [])
                        if m
                    }
                new_files = disk_files - indexed_files
                if new_files:
                    logger.info(f"New documents detected: {new_files} — clearing and re-indexing from {docs_dir}")
                    # Clear existing entries without touching the collection object itself
                    if collection.count() > 0:
                        all_ids = collection.get()["ids"]
                        if all_ids:
                            collection.delete(ids=all_ids)
                    count = load_documents_from_directory(str(docs_dir), collection, settings)
                    logger.info(f"Auto-indexed {count} document(s) from {docs_dir}")
                else:
                    logger.info(f"All {len(disk_files)} document(s) already indexed: {disk_files}")

        # Step 3: LlamaIndex — build index from ChromaDB data (now includes all files)
        logger.info("Building LlamaIndex VectorStoreIndex...")
        index = build_vector_store_index(collection)
        app.state.vector_index = index               # May be None if no docs indexed yet

        # Step 4: LLM — initialise the chat model
        logger.info("Initialising LLM client...")
        llm = get_llm(settings)
        app.state.llm = llm

        # Step 5: Tools — create the e-commerce tool functions for the agent
        logger.info("Initialising e-commerce tools...")
        tools = get_tools(ecommerce_base_url=settings.ecommerce_api_url)
        app.state.tools = tools

        # Step 6: LangGraph — build and compile the conversation graph (with tools)
        logger.info("Building LangGraph conversation graph...")
        compiled_graph = build_conversation_graph(
            llm=llm,
            index=index,
            settings=settings,
            tools=tools,
        )
        app.state.compiled_graph = compiled_graph

        logger.info("All services initialised. Server is ready to accept requests.")

    except Exception as e:
        logger.error(f"STARTUP FAILED: {e}", exc_info=True)
        logger.error(
            "Check your .env file: ensure OPENAI_API_KEY (or Azure equivalents) "
            "and CHROMA_PERSIST_PATH are set correctly."
        )
        # Re-raise so the server fails loudly rather than accepting requests
        # with broken services behind the scenes
        raise

    # ── The app is now running — yield hands control to FastAPI ──────────
    yield

    # ── SHUTDOWN ──────────────────────────────────────────────────────────
    logger.info("Shutting down LLM Chatbot Backend...")
    # ChromaDB PersistentClient flushes to disk automatically on process exit
    # No explicit cleanup needed for the LLM client (it uses HTTP)
    logger.info("Shutdown complete.")


# ── Create the FastAPI application ────────────────────────────────────────────
app = FastAPI(
    title="LLM Chatbot Backend",
    description=(
        "Production-grade FastAPI chatbot using LangChain, LangGraph, "
        "LlamaIndex, ChromaDB, and OpenAI/Azure OpenAI."
    ),
    version="1.0.0",
    lifespan=lifespan,
    # OpenAPI docs are available at /docs (Swagger UI) and /redoc
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS middleware ────────────────────────────────────────────────────────────
# CORS = Cross-Origin Resource Sharing.
# This allows web frontends (React, Vue, etc.) on different domains to call our API.
# In production, replace "*" with your specific frontend domain for security.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production: ["https://your-frontend.azurewebsites.net"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include routers ────────────────────────────────────────────────────────────
# Each router handles a group of related endpoints.
# Including them here registers all their routes with the FastAPI app.
app.include_router(health_router.router)
app.include_router(chat_router.router)


# ── Root redirect ───────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API docs for discoverability."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
