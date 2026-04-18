# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# Unit tests for the RAG retrieval logic in app/rag/retriever.py.
# Tests verify that:
#   - Context is retrieved when the index is populated
#   - Empty results are handled gracefully
#   - Errors from ChromaDB are caught and don't crash the server
# ─────────────────────────────────────────────────────────────────────────────

import pytest
from unittest.mock import MagicMock

from app.rag.retriever import retrieve_context, RetrievalResult


class TestRetrieveContext:
    """Tests for the retrieve_context() function."""

    def test_returns_empty_result_when_index_is_none(self, test_settings):
        """
        WHAT: Tests behaviour when no VectorStoreIndex is available (index=None).
        WHY:  The system must work before any documents are indexed.
              retrieve_context should return a graceful empty result, not raise.
        """
        result = retrieve_context(
            query="What is the return policy?",
            index=None,
            settings=test_settings,
        )

        # Should return a valid RetrievalResult with no sources
        assert isinstance(result, RetrievalResult)
        assert result.chunks_found == 0
        assert result.sources == []
        assert result.context_text  # Should have some explanatory text

    def test_returns_context_when_chunks_found(self, test_settings, mock_index):
        """
        WHAT: Tests that retrieved chunks are formatted into the context string.
        WHY:  The context string is what gets injected into the LLM prompt.
              It must contain the chunk text and source attribution.
        """
        result = retrieve_context(
            query="What is artificial intelligence?",
            index=mock_index,
            settings=test_settings,
        )

        assert isinstance(result, RetrievalResult)
        assert result.chunks_found > 0
        assert len(result.sources) > 0
        assert "test_document.txt" in result.sources
        # Context should contain the chunk text we set up in the mock
        assert "test document content" in result.context_text

    def test_returns_empty_when_no_chunks_found(self, test_settings):
        """
        WHAT: Tests behaviour when ChromaDB finds no similar chunks.
        WHY:  Not every question will have a relevant document.
              The system should fall back to general LLM knowledge gracefully.
        """
        mock_index = MagicMock()
        mock_retriever = MagicMock()
        # Return empty list (no similar chunks found)
        mock_retriever.retrieve.return_value = []
        mock_index.as_retriever.return_value = mock_retriever

        result = retrieve_context(
            query="Completely unrelated topic",
            index=mock_index,
            settings=test_settings,
        )

        assert result.chunks_found == 0
        assert result.sources == []

    def test_handles_retriever_exception_gracefully(self, test_settings):
        """
        WHAT: Tests that ChromaDB errors are caught and don't raise exceptions.
        WHY:  External service failures (ChromaDB crash, network timeout) must
              not crash the API. We return an empty result so the LLM can still
              respond from general knowledge.
        """
        mock_index = MagicMock()
        mock_retriever = MagicMock()
        # Simulate a ChromaDB crash
        mock_retriever.retrieve.side_effect = Exception("ChromaDB connection refused")
        mock_index.as_retriever.return_value = mock_retriever

        # Should NOT raise an exception — must return a RetrievalResult
        result = retrieve_context(
            query="What happened?",
            index=mock_index,
            settings=test_settings,
        )

        assert isinstance(result, RetrievalResult)
        assert result.chunks_found == 0

    def test_respects_top_k_setting(self, test_settings):
        """
        WHAT: Tests that as_retriever is called with the correct similarity_top_k.
        WHY:  top_k controls how many chunks are retrieved.
              If this is wrong, we either send too much context (high cost)
              or too little (poor answers).
        """
        mock_index = MagicMock()
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = []
        mock_index.as_retriever.return_value = mock_retriever

        retrieve_context(
            query="test query",
            index=mock_index,
            settings=test_settings,
        )

        # Verify as_retriever was called with the correct top_k from settings
        mock_index.as_retriever.assert_called_once_with(
            similarity_top_k=test_settings.rag_top_k
        )

    def test_source_deduplication(self, test_settings):
        """
        WHAT: Tests that duplicate source file names are deduplicated in results.
        WHY:  Multiple chunks can come from the same document.
              The sources list should contain each document name only once
              to avoid confusing the user with duplicate citations.
        """
        mock_index = MagicMock()
        mock_retriever = MagicMock()

        # Create two chunks from the SAME source document
        def make_mock_node(content: str, source: str, score: float):
            node = MagicMock()
            node.node.metadata = {"file_name": source}
            node.node.get_content.return_value = content
            node.score = score
            return node

        mock_retriever.retrieve.return_value = [
            make_mock_node("Chunk 1 content", "policy.txt", 0.95),
            make_mock_node("Chunk 2 content", "policy.txt", 0.88),  # Same source!
        ]
        mock_index.as_retriever.return_value = mock_retriever

        result = retrieve_context(
            query="policy question",
            index=mock_index,
            settings=test_settings,
        )

        # Despite 2 chunks from the same file, sources should list it only once
        assert result.sources.count("policy.txt") == 1
