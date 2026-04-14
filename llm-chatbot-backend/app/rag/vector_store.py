# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file sets up ChromaDB as the vector store and integrates it with LlamaIndex.
# ChromaDB stores document "embeddings" — numerical representations of text.
# When you ask a question, ChromaDB finds the most similar stored chunks.
# Think of it as a search engine that understands meaning, not just keywords.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.config import Settings

logger = logging.getLogger(__name__)


def get_chroma_client(settings: Settings) -> chromadb.ClientAPI:
    """
    Creates and returns a ChromaDB client.

    Uses EphemeralClient (in-memory) when settings.chroma_in_memory is True —
    suitable for Azure Container Apps where disk state resets on restart.
    Uses PersistentClient otherwise (local development with disk persistence).

    Args:
        settings: Application settings containing the ChromaDB configuration.

    Returns:
        chromadb.ClientAPI: A connected ChromaDB client.

    Raises:
        Exception: If ChromaDB cannot initialise (e.g., bad path permissions).
    """
    try:
        if settings.chroma_in_memory:
            logger.info("Initialising ChromaDB as EphemeralClient (in-memory, no persistence)")
            client = chromadb.EphemeralClient(
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        else:
            logger.info(f"Initialising ChromaDB at path: {settings.chroma_persist_path}")
            client = chromadb.PersistentClient(
                path=settings.chroma_persist_path,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        logger.info("ChromaDB client initialised successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialise ChromaDB: {e}")
        raise


def get_or_create_collection(
    client: chromadb.ClientAPI,
    settings: Settings,
) -> chromadb.Collection:
    """
    Gets an existing ChromaDB collection or creates it if it doesn't exist.

    WHAT IS A COLLECTION?
      A collection in ChromaDB is like a table in a relational database.
      All our document embeddings go into one collection.
      "get_or_create" is idempotent — safe to call multiple times.

    Args:
        client:   The ChromaDB client from get_chroma_client().
        settings: Application settings containing the collection name.

    Returns:
        chromadb.Collection: The collection object for storing/querying vectors.
    """
    logger.info(f"Getting or creating collection: {settings.chroma_collection_name}")
    return client.get_or_create_collection(
        name=settings.chroma_collection_name,
        # cosine distance is best for semantic similarity of text embeddings
        metadata={"hnsw:space": "cosine"},
    )


def build_vector_store_index(
    collection: chromadb.Collection,
) -> Optional[VectorStoreIndex]:
    """
    Wraps a ChromaDB collection inside a LlamaIndex VectorStoreIndex.

    WHY LLAMAINDEX WRAPS CHROMADB?
      ChromaDB is the raw storage. LlamaIndex adds:
        - Document loading and chunking
        - Automatic embedding generation
        - A high-level query interface
      Together they form the RAG pipeline.

    Args:
        collection: The ChromaDB collection containing indexed documents.

    Returns:
        VectorStoreIndex | None: A LlamaIndex index if the collection has data,
                                  or None if the collection is empty.
    """
    try:
        # Wrap the ChromaDB collection in LlamaIndex's abstraction
        vector_store = ChromaVectorStore(chroma_collection=collection)

        # StorageContext tells LlamaIndex to use our ChromaDB as the backend
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Check if collection has any documents before building index
        if collection.count() == 0:
            logger.warning(
                "ChromaDB collection is empty. "
                "Call POST /api/v1/index to add documents before querying."
            )
            return None

        logger.info(f"Building VectorStoreIndex from {collection.count()} stored chunks")
        # VectorStoreIndex.from_vector_store connects to the existing data
        # (it does NOT re-embed — embeddings are already in ChromaDB)
        return VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context,
        )
    except Exception as e:
        logger.error(f"Failed to build VectorStoreIndex: {e}")
        raise
