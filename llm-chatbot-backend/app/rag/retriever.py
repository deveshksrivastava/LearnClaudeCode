# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file queries ChromaDB to find document chunks relevant to a user's question.
# This is the "R" in RAG — Retrieval. Given a question, it finds the most
# semantically similar chunks stored in ChromaDB and returns them as plain text.
# The retrieved text becomes the "context" injected into the LLM prompt.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from dataclasses import dataclass
from typing import List, Optional

from llama_index.core import VectorStoreIndex
from llama_index.core.schema import NodeWithScore

from app.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """
    Container for retrieved document chunks and their source information.

    WHY A DATACLASS?
      A dataclass is a simple class that holds data — no logic, just structure.
      It's cleaner than a plain dict because you get type hints and autocomplete.

    Attributes:
        context_text: All retrieved chunks concatenated into one string.
                      This is what gets injected into the LLM prompt.
        sources:      List of source document names (used to cite sources in response).
        chunks_found: How many chunks were retrieved.
    """
    context_text: str
    sources: List[str]
    chunks_found: int


def retrieve_context(
    query: str,
    index: Optional[VectorStoreIndex],
    settings: Settings,
) -> RetrievalResult:
    """
    Queries ChromaDB to find the most relevant document chunks for a query.

    HOW IT WORKS:
      1. The query string is converted to an embedding vector (via OpenAI API)
      2. ChromaDB finds the top-k stored chunks with the most similar vectors
      3. Those chunks are returned as plain text context for the LLM

    WHAT IS "TOP-K"?
      top_k = 3 means "find the 3 most similar chunks."
      Higher k = more context but also more noise and higher LLM token costs.

    Args:
        query:    The user's question to search for relevant chunks.
        index:    The LlamaIndex VectorStoreIndex wrapping our ChromaDB collection.
                  Can be None if no documents have been indexed yet.
        settings: Application settings (contains rag_top_k).

    Returns:
        RetrievalResult: Contains the context text, source names, and chunk count.
                         Returns empty result if index is None or retrieval fails.
    """
    # If no documents have been indexed yet, return an empty result gracefully
    # The LangGraph node will then use a simple prompt without RAG context
    if index is None:
        logger.warning("No VectorStoreIndex available — skipping RAG retrieval")
        return RetrievalResult(
            context_text="No documents have been indexed yet.",
            sources=[],
            chunks_found=0,
        )

    try:
        logger.info(f"Retrieving top-{settings.rag_top_k} chunks for query: '{query[:80]}...'")

        # Create a retriever from the index
        # similarity_top_k tells ChromaDB how many chunks to return
        retriever = index.as_retriever(similarity_top_k=settings.rag_top_k)

        # .retrieve() converts the query to a vector and does the similarity search
        nodes: List[NodeWithScore] = retriever.retrieve(query)

        if not nodes:
            logger.info("No relevant chunks found in ChromaDB for this query")
            return RetrievalResult(
                context_text="No relevant documents found for this query.",
                sources=[],
                chunks_found=0,
            )

        # Format each retrieved chunk for injection into the prompt
        context_parts = []
        sources = []

        for i, node_with_score in enumerate(nodes, start=1):
            node = node_with_score.node
            score = node_with_score.score or 0.0

            # Extract source file name from node metadata (set by LlamaIndex during indexing)
            source_name = node.metadata.get("file_name", f"chunk_{i}")

            chunk_text = node.get_content()
            context_parts.append(
                f"[Source {i}: {source_name} (similarity: {score:.2f})]\n{chunk_text}"
            )
            if source_name not in sources:
                sources.append(source_name)

            logger.debug(f"  Chunk {i}: {source_name} (score={score:.3f})")

        # Join all chunks into one context block, separated by blank lines
        context_text = "\n\n".join(context_parts)
        logger.info(f"Retrieved {len(nodes)} chunks from {len(sources)} source(s)")

        return RetrievalResult(
            context_text=context_text,
            sources=sources,
            chunks_found=len(nodes),
        )

    except Exception as e:
        logger.error(f"RAG retrieval failed for query '{query[:80]}': {e}")
        # Return empty result instead of crashing — the LLM can still answer
        # without RAG context (just won't have document knowledge)
        return RetrievalResult(
            context_text="Context retrieval failed. Answering from general knowledge.",
            sources=[],
            chunks_found=0,
        )
