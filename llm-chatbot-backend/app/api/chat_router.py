# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file defines the main chat endpoint and the document indexing endpoint.
# POST /api/v1/chat-llm  → runs the LangGraph conversation graph and returns a response
# POST /api/v1/index → loads documents from a folder into ChromaDB
#
# FastAPI routers keep endpoint logic separated by feature area.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from app.models import (
    ChatRequest, ChatResponse,
    IndexRequest, IndexResponse,
    UploadResponse, DocumentListResponse, DeleteDocumentResponse,
)
from app.config import Settings, get_settings
from app.graph.graph_builder import run_conversation_graph, build_conversation_graph
from app.rag.document_loader import load_documents_from_directory, SUPPORTED_EXTENSIONS
from app.rag.vector_store import build_vector_store_index

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat-llm"])

# In-memory session store: maps session_id → list of message dicts
# WHY IN-MEMORY? Simple and fast for demonstrations.
# In production, replace with Redis or Azure Cache for Redis for persistence
# across multiple server instances.
_session_store: dict[str, list[dict]] = {}

# Path to the directory where uploaded documents are stored.
# Defined at module level so tests can monkeypatch it.
DOCS_DIR = Path(__file__).parent.parent.parent / "data" / "sample_docs"


@router.post(
    "/chat-llm",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message",
    description=(
        "Send a message to the chatbot. The bot uses RAG to search indexed "
        "documents and LangGraph for multi-turn conversation memory."
    ),
)
async def chat(
    request_body: ChatRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> ChatResponse:
    """
    POST /api/v1/chat-llm — main chat endpoint.

    HOW THIS WORKS:
      1. Look up (or create) the session's message history
      2. Run the LangGraph graph with the current message + history
      3. Save the updated history back to the session store
      4. Return the LLM's response and source documents

    WHY request: Request?
      We access app.state (set during startup in main.py) to get the
      compiled LangGraph graph. Using request.app.state avoids global variables.

    Args:
        request_body: Validated ChatRequest (session_id + message).
        request:      The raw FastAPI Request object (used to access app.state).
        settings:     Application settings (injected by FastAPI).

    Returns:
        ChatResponse: The bot's reply and source document names.

    Raises:
        HTTPException 503: If the LangGraph graph is not initialised.
        HTTPException 500: If graph execution fails unexpectedly.
    """
    session_id = request_body.session_id
    user_message = request_body.message

    logger.info(f"POST /chat-llm — session='{session_id}', message='{user_message[:60]}'")
    logger.log(logging.DEBUG, f"DEVESH - POST /chat-llm — session='{session_id}', message='{user_message[:60]}'")
    print(f"POST /chat-llm — session='{session_id}', message='{user_message[:60]}'")

    # Retrieve the compiled graph from app state (set during startup in main.py)
    compiled_graph = getattr(request.app.state, "compiled_graph", None)
    if compiled_graph is None:
        logger.error("Compiled graph not found in app.state — startup may have failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot service is not ready. Check server logs for startup errors.",
        )

    # Get existing message history for this session, or start fresh
    message_history = _session_store.get(session_id, [])

    try:
        # Run the full LangGraph pipeline for this turn
        final_state = run_conversation_graph(
            compiled_graph=compiled_graph,
            session_id=session_id,
            user_input=user_message,
            message_history=message_history,
        )
    except Exception as e:
        logger.error(f"Graph execution failed for session '{session_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while processing your message.",
        )

    # Check if the graph itself returned an error state
    if final_state.get("error") and not final_state.get("final_response"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=final_state["error"],
        )

    # Save the updated conversation history (now includes this turn)
    _session_store[session_id] = final_state.get("messages", [])

    return ChatResponse(
        session_id=session_id,
        response=final_state.get("final_response", "No response generated."),
        sources=final_state.get("sources", []),
    )


@router.post(
    "/index",
    response_model=IndexResponse,
    status_code=status.HTTP_200_OK,
    summary="Index documents into ChromaDB",
    description=(
        "Load .txt or .pdf files from a directory into the ChromaDB vector store. "
        "After indexing, the chat endpoint can use these documents for RAG."
    ),
)
async def index_documents(
    request_body: IndexRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> IndexResponse:
    """
    POST /api/v1/index — document indexing endpoint.

    WHAT THIS DOES:
      1. Validates the directory path
      2. Loads .txt/.pdf files and splits them into chunks
      3. Generates embeddings for each chunk (via OpenAI Embeddings API)
      4. Stores the embeddings in ChromaDB

    After this runs, the /chat endpoint can use the indexed documents for RAG.

    Args:
        request_body: Validated IndexRequest (directory path).
        request:      FastAPI Request to access app.state.
        settings:     Application settings.

    Returns:
        IndexResponse: Number of indexed documents and a summary message.

    Raises:
        HTTPException 400: If the directory doesn't exist or has no supported files.
        HTTPException 500: If indexing fails unexpectedly.
    """
    directory = request_body.directory
    logger.info(f"POST /index — directory='{directory}'")

    # Always get a fresh collection reference from the client to avoid stale UUID errors
    chroma_client = getattr(request.app.state, "chroma_client", None)
    if chroma_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ChromaDB is not ready. Check server logs.",
        )
    collection = chroma_client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    # Keep app.state in sync with the fresh reference
    request.app.state.chroma_collection = collection

    try:
        indexed_count = load_documents_from_directory(
            directory=directory,
            collection=collection,
            settings=settings,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Indexing failed for directory '{directory}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Indexing failed: {str(e)}",
        )

    return IndexResponse(
        indexed=indexed_count,
        message=f"Successfully indexed {indexed_count} document(s) from '{directory}'",
    )


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List indexed documents",
    description="Returns the filenames of all supported files currently in data/sample_docs/.",
)
async def list_documents(
    settings: Settings = Depends(get_settings),
) -> DocumentListResponse:
    if not DOCS_DIR.exists():
        return DocumentListResponse(documents=[])
    files = sorted(
        f.name for f in DOCS_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    return DocumentListResponse(documents=files)
