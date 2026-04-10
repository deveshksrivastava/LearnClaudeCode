# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file defines the "shape" of data going IN and OUT of the API.
# Pydantic models are like contracts: they guarantee that the API receives
# exactly the fields it expects and returns exactly what was promised.
# If the caller sends wrong data, Pydantic returns a clear 422 error
# automatically — no manual validation code needed.
# ─────────────────────────────────────────────────────────────────────────────

from pydantic import BaseModel, Field
from typing import Optional


# ── /api/v1/chat ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """
    Request body for POST /api/v1/chat.

    Fields:
        session_id: A unique string that identifies this conversation.
                    The same session_id across multiple requests = same conversation.
                    Think of it like a conversation thread ID.
        message:    The user's latest message to the chatbot.
    """
    session_id: str = Field(
        ...,  # "..." means this field is REQUIRED — no default value
        min_length=1,
        max_length=128,
        description="Unique identifier for the conversation session",
        examples=["user-123-session-456"],
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="The user's message to send to the chatbot",
        examples=["What is the return policy for electronics?"],
    )


class ChatResponse(BaseModel):
    """
    Response body for POST /api/v1/chat.

    Fields:
        session_id: Echoed back so the client knows which session this belongs to.
        response:   The chatbot's reply to the user's message.
        sources:    Names of document chunks that were used to build the answer.
                    Empty list means no RAG documents were used (general LLM knowledge).
    """
    session_id: str = Field(description="The session ID from the request")
    response: str = Field(description="The chatbot's reply")
    sources: list[str] = Field(
        default_factory=list,   # Default to empty list, not None
        description="Names of source documents used in the RAG retrieval step",
    )


# ── /api/v1/health ──────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """
    Response body for GET /api/v1/health.

    This endpoint is used by Azure Container Apps (and load balancers)
    to check if the service is alive. Must respond quickly (< 1 second).

    Fields:
        status:  Always "ok" when the service is healthy.
        version: The application version string from config.
    """
    status: str = Field(default="ok", description="Health status of the service")
    version: str = Field(description="Current application version")


# ── /api/v1/index ───────────────────────────────────────────────────────────

class IndexRequest(BaseModel):
    """
    Request body for POST /api/v1/index.

    This endpoint triggers the RAG indexing pipeline:
    it reads documents from a folder and loads them into ChromaDB.

    Fields:
        directory: Path to a folder containing .txt or .pdf files to index.
                   On Azure, this would typically be a mounted volume path.
    """
    directory: str = Field(
        ...,
        min_length=1,
        description="Path to the folder containing documents to index",
        examples=["./data/sample_docs"],
    )


class IndexResponse(BaseModel):
    """
    Response body for POST /api/v1/index.

    Fields:
        indexed: How many documents were successfully indexed.
        message: Human-readable summary of what happened.
    """
    indexed: int = Field(description="Number of documents successfully indexed")
    message: str = Field(description="Human-readable result message")


# ── Error response (used in error handlers) ──────────────────────────────────

class ErrorResponse(BaseModel):
    """
    Standard error response shape.
    FastAPI's HTTPException already returns JSON, but this model
    documents the shape for API clients.

    Fields:
        detail: A human-readable error message.
    """
    detail: str = Field(description="Error message describing what went wrong")
