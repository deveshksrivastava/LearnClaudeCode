# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file defines ALL configuration for the application.
# Instead of scattering "magic strings" like "gpt-4" or port numbers
# throughout the code, we centralise everything here.
# pydantic-settings reads values from environment variables (or .env file)
# and validates them — so if a required variable is missing, you get a clear
# error at startup rather than a cryptic crash deep in the code.
# ─────────────────────────────────────────────────────────────────────────────

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    pydantic-settings automatically reads from:
      1. Actual environment variables (highest priority)
      2. A .env file in the current working directory
      3. Default values defined here (lowest priority)

    This means in production (Azure) you set real env vars.
    In local development you use a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",          # Load from .env file if it exists
        env_file_encoding="utf-8",
        case_sensitive=False,     # OPENAI_API_KEY and openai_api_key both work
        extra="ignore",           # Silently ignore unknown env vars
    )

    # ── LLM Provider Selection ─────────────────────────────────────────────
    llm_provider: str = Field(
        default="openai",
        description="Which LLM provider to use: 'openai' or 'azure'",
    )

    # ── Standard OpenAI settings ───────────────────────────────────────────
    openai_api_key: str = Field(
        default="",
        description="API key for OpenAI (api.openai.com). Leave empty if using Azure.",
    )
    openai_model_name: str = Field(
        default="gpt-4o-mini",
        description="Which OpenAI chat model to use (e.g. gpt-4o-mini, gpt-4o)",
    )
    openai_embedding_model: str = Field(
        default="text-embedding-ada-002",
        description="Which OpenAI embedding model to use for ChromaDB indexing",
    )

    # ── Azure OpenAI settings ──────────────────────────────────────────────
    azure_openai_api_key: str = Field(
        default="",
        description="API key for Azure OpenAI Service",
    )
    azure_openai_endpoint: str = Field(
        default="",
        description="Full URL of your Azure OpenAI resource (e.g. https://name.openai.azure.com/)",
    )
    azure_openai_deployment_name: str = Field(
        default="gpt-4o",
        description="Name of the deployment in Azure OpenAI Studio",
    )
    azure_openai_api_version: str = Field(
        default="2024-02-01",
        description="Azure OpenAI REST API version",
    )
    azure_openai_embedding_deployment: str = Field(
        default="text-embedding-ada-002",
        description="Name of the embedding deployment in Azure OpenAI Studio",
    )

    # ── LLM Behaviour ──────────────────────────────────────────────────────
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,   # Must be >= 0.0 (ge = greater-than-or-equal)
        le=2.0,   # Must be <= 2.0 (le = less-than-or-equal)
        description="Temperature controls randomness. 0=deterministic, 2=very random.",
    )
    llm_max_tokens: int = Field(
        default=1024,
        gt=0,     # Must be > 0
        description="Maximum number of tokens the LLM can generate in one response.",
    )

    # ── ChromaDB ───────────────────────────────────────────────────────────
    chroma_persist_path: str = Field(
        default="./chroma_data",
        description="File system path where ChromaDB stores its vector data",
    )
    chroma_collection_name: str = Field(
        default="chatbot_docs",
        description="Name of the ChromaDB collection (like a table) for our documents",
    )
    chroma_host: str = Field(
        default="localhost",
        description="ChromaDB server host (used when running ChromaDB as a service)",
    )
    chroma_port: int = Field(
        default=8001,
        description="ChromaDB server port",
    )

    # ── Application ────────────────────────────────────────────────────────
    app_version: str = Field(
        default="1.0.0",
        description="Application version string (shown in /health endpoint)",
    )
    log_level: str = Field(
        default="INFO",
        description="Python logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
    )
    app_port: int = Field(
        default=8000,
        description="Port the FastAPI server listens on",
    )

    # ── RAG settings ───────────────────────────────────────────────────────
    rag_top_k: int = Field(
        default=6,
        description="How many document chunks to retrieve from ChromaDB per query",
    )
    rag_chunk_size: int = Field(
        default=512,
        description="Size of each text chunk (in tokens) when splitting documents",
    )
    rag_chunk_overlap: int = Field(
        default=50,
        description="How many tokens overlap between consecutive chunks (prevents losing context at chunk boundaries)",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Returns the application settings, cached after the first call.

    WHY lru_cache?
      Creating a Settings object reads from disk (.env file) and validates
      all values. We only want to do this once — not on every request.
      lru_cache makes subsequent calls return the same object instantly.

    Returns:
        Settings: The validated, populated configuration object.
    """
    return Settings()
