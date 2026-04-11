# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file handles loading documents (.txt, .pdf) from disk into LlamaIndex.
# "Loading" means: read file → split into chunks → generate embeddings → store in ChromaDB.
# Think of it as the "ingestion pipeline" that populates our knowledge base.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from pathlib import Path
from typing import List

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings as LlamaSettings,
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
import chromadb

from app.config import Settings

logger = logging.getLogger(__name__)

# File extensions we support for indexing
SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".md"}


def configure_llama_settings(settings: Settings) -> None:
    """
    Configures LlamaIndex's global settings for embedding and chunking.

    WHY GLOBAL SETTINGS?
      LlamaIndex uses a global Settings object (similar to Django settings).
      We configure it once at startup so all indexing/querying uses the same
      embedding model and chunk sizes consistently.

    Args:
        settings: Application settings with embedding model name and chunk config.
    """
    # Set the embedding model — this is what converts text chunks into vectors
    LlamaSettings.embed_model = OpenAIEmbedding(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key or None,  # type: ignore[arg-type]
    )

    # SentenceSplitter splits long documents into smaller chunks.
    # WHY CHUNK? LLMs have context window limits — we can't send a 100-page PDF.
    # Chunking breaks it into pieces that fit, and we only send RELEVANT pieces.
    LlamaSettings.node_parser = SentenceSplitter(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,  # Overlap prevents losing context at boundaries
    )


def load_documents_from_directory(
    directory: str,
    collection: chromadb.Collection,
    settings: Settings,
) -> int:
    """
    Loads all supported documents from a directory into ChromaDB via LlamaIndex.

    STEP-BY-STEP FLOW:
      1. Scan directory for .txt/.pdf/.md files
      2. Read each file into LlamaIndex Document objects
      3. Split each Document into chunks (nodes)
      4. Generate an embedding vector for each chunk (via OpenAI Embeddings API)
      5. Store all vectors + metadata in ChromaDB

    Args:
        directory: Path to the folder containing documents to index.
        collection: The ChromaDB collection to store embeddings in.
        settings:   Application settings (for embedding config).

    Returns:
        int: The number of documents successfully indexed.

    Raises:
        FileNotFoundError: If the directory does not exist.
        ValueError:        If no supported documents are found.
        Exception:         For any LlamaIndex or ChromaDB errors during indexing.
    """
    dir_path = Path(directory)

    # Validate the directory exists before attempting anything
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    # Check that we actually have files to load
    found_files = _find_supported_files(dir_path)
    if not found_files:
        raise ValueError(
            f"No supported files ({', '.join(SUPPORTED_EXTENSIONS)}) "
            f"found in directory: {directory}"
        )

    logger.info(f"Found {len(found_files)} documents to index: {[f.name for f in found_files]}")

    try:
        # Configure LlamaIndex before loading (sets embedding model + chunker)
        configure_llama_settings(settings)

        # SimpleDirectoryReader reads all supported files from the directory
        reader = SimpleDirectoryReader(
            input_dir=str(dir_path),
            required_exts=list(SUPPORTED_EXTENSIONS),
            recursive=True,  # Also index files in sub-folders
        )
        documents = reader.load_data()
        logger.info(f"Loaded {len(documents)} document(s) into LlamaIndex")

        # Wrap ChromaDB collection in LlamaIndex's vector store abstraction
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # from_documents does the heavy lifting:
        #   parse → chunk → embed → store in ChromaDB
        VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=False,  # Set True locally to see a progress bar
        )

        logger.info(f"Successfully indexed {len(documents)} document(s) into ChromaDB")
        return len(documents)

    except Exception as e:
        logger.error(f"Failed to index documents from '{directory}': {e}")
        raise


def _find_supported_files(dir_path: Path) -> List[Path]:
    """
    Scans a directory and returns a list of files with supported extensions.

    Args:
        dir_path: The directory to scan.

    Returns:
        List[Path]: List of file paths with supported extensions.
    """
    return [
        f for f in dir_path.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
