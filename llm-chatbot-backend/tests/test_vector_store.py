# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# Tests for the vector store module (app/rag/vector_store.py).
# These tests verify that ChromaDB client creation works correctly in both
# persistent (disk) and ephemeral (in-memory) modes.
# ─────────────────────────────────────────────────────────────────────────────

from unittest.mock import patch, MagicMock
from app.config import Settings


def test_get_chroma_client_persistent_by_default():
    """
    WHAT: Tests that get_chroma_client uses PersistentClient by default.
    WHY:  Default behaviour should be disk persistence for local development.
          This test ensures the function correctly initialises a PersistentClient
          when chroma_in_memory is False.
    """
    settings = Settings(chroma_in_memory=False, chroma_persist_path="./test_chroma")
    with patch("app.rag.vector_store.chromadb.PersistentClient") as mock_persistent, \
         patch("app.rag.vector_store.chromadb.EphemeralClient") as mock_ephemeral:
        mock_persistent.return_value = MagicMock()
        from app.rag.vector_store import get_chroma_client
        get_chroma_client(settings)
        mock_persistent.assert_called_once()
        mock_ephemeral.assert_not_called()


def test_get_chroma_client_ephemeral_when_in_memory():
    """
    WHAT: Tests that get_chroma_client uses EphemeralClient when chroma_in_memory=True.
    WHY:  Azure Container Apps need stateless operation with in-memory storage.
          This test ensures the function correctly switches to EphemeralClient
          when the in-memory flag is enabled.
    """
    settings = Settings(chroma_in_memory=True)
    with patch("app.rag.vector_store.chromadb.EphemeralClient") as mock_ephemeral, \
         patch("app.rag.vector_store.chromadb.PersistentClient") as mock_persistent:
        mock_ephemeral.return_value = MagicMock()
        from app.rag.vector_store import get_chroma_client
        get_chroma_client(settings)
        mock_ephemeral.assert_called_once()
        mock_persistent.assert_not_called()
