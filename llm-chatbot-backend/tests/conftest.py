# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# conftest.py is pytest's special file for shared test fixtures.
# A "fixture" is a reusable piece of test setup that pytest injects into tests.
# Instead of creating a mock LLM in every test file, we define it once here
# and pytest shares it across all test files automatically.
# ─────────────────────────────────────────────────────────────────────────────

import pytest
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from app.config import Settings
from app.api import chat_router, health_router


@pytest.fixture
def test_settings() -> Settings:
    """
    Returns a Settings object with safe test values.

    WHY NOT USE REAL SETTINGS?
      Tests should not require a real OpenAI key or a running ChromaDB.
      Using fake values ensures tests are:
        - Fast (no network calls)
        - Free (no API costs)
        - Deterministic (no flaky failures from external services)
        - Safe to run in CI/CD pipelines

    Returns:
        Settings: A Settings object populated with test-safe values.
    """
    return Settings(
        llm_provider="openai",
        openai_api_key="sk-test-fake-key-for-testing-only",
        openai_model_name="gpt-4o-mini",
        openai_embedding_model="text-embedding-ada-002",
        llm_temperature=0.0,    # Deterministic for tests
        llm_max_tokens=256,
        chroma_persist_path="./test_chroma_data",
        chroma_collection_name="test_collection",
        app_version="1.0.0-test",
        log_level="WARNING",    # Less noise during tests
        rag_top_k=2,
        rag_chunk_size=256,
        rag_chunk_overlap=20,
    )


@pytest.fixture
def mock_llm():
    """
    Returns a mock LangChain LLM that returns a predictable response.

    WHY MOCK THE LLM?
      We don't want tests to make real OpenAI API calls because:
        - They cost money per token
        - They require a real API key in CI
        - They are slow (network latency)
        - They can fail for reasons unrelated to our code

    The mock returns a fixed AIMessage so our node tests can assert
    that the response was correctly processed.

    Returns:
        MagicMock: A mock object that behaves like a LangChain BaseChatModel.
    """
    mock = MagicMock()
    # Make .invoke() return a real AIMessage object (the same type the real LLM returns)
    mock.invoke.return_value = AIMessage(
        content="This is a test response from the mock LLM."
    )
    return mock


@pytest.fixture
def mock_index():
    """
    Returns a mock LlamaIndex VectorStoreIndex.

    WHY MOCK THE INDEX?
      The real VectorStoreIndex requires ChromaDB and embeddings.
      We mock it to return a predictable retriever that doesn't hit ChromaDB.

    Returns:
        MagicMock: A mock VectorStoreIndex.
    """
    mock = MagicMock()

    # Create a mock node (chunk of text) that the retriever would return
    mock_node = MagicMock()
    mock_node.node.metadata = {"file_name": "test_document.txt"}
    mock_node.node.get_content.return_value = "This is test document content about AI."
    mock_node.score = 0.95

    # Make the retriever return our mock node
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [mock_node]
    mock.as_retriever.return_value = mock_retriever

    return mock


@pytest.fixture
def mock_empty_index():
    """
    Returns None to simulate "no index available" (empty collection).

    Used to test the "no documents indexed yet" code path.

    Returns:
        None: The code treats None as "no index available".
    """
    return None


@pytest.fixture
def sample_conversation_state() -> dict:
    """
    Returns a minimal valid ConversationState for testing graph nodes.

    Returns:
        dict: A state dict with all required fields populated.
    """
    return {
        "session_id": "test-session-001",
        "messages": [],
        "user_input": "What is the return policy?",
        "retrieved_context": "",
        "sources": [],
        "final_response": "",
        "error": None,
    }


@pytest.fixture
def test_client():
    """
    Returns a FastAPI TestClient with all external dependencies mocked.

    HOW IT WORKS:
      We create a fresh FastAPI test app with a no-op lifespan that
      populates app.state with mock objects. This completely bypasses
      real startup (no ChromaDB, no OpenAI connections).

    WHY A SEPARATE test_app INSTEAD OF THE REAL app?
      The real app's lifespan tries to connect to OpenAI and ChromaDB.
      In tests, we replace the whole lifespan with a mock that just
      sets the state directly. This approach avoids complex patching.

    Yields:
        TestClient: A configured test client.
    """
    # Build a mock compiled graph with a realistic return value
    mock_compiled_graph = MagicMock()
    mock_compiled_graph.invoke.return_value = {
        "session_id": "test-session-001",
        "messages": [
            {"role": "human", "content": "Hello"},
            {"role": "assistant", "content": "Hi there! How can I help?"},
        ],
        "user_input": "Hello",
        "retrieved_context": "Test context",
        "sources": ["doc1.txt"],
        "final_response": "Hi there! How can I help?",
        "error": None,
    }

    mock_collection = MagicMock()
    mock_collection.count.return_value = 5

    # Define a no-op lifespan that sets mock state on the test app
    @asynccontextmanager
    async def mock_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """
        Replaces the real startup with direct state injection.
        Code before yield runs at startup; after yield runs at shutdown.
        """
        app.state.compiled_graph = mock_compiled_graph
        app.state.chroma_collection = mock_collection
        app.state.chroma_client = MagicMock()
        app.state.vector_index = MagicMock()
        app.state.llm = MagicMock()
        yield
        # No cleanup needed for mocks

    # Build a minimal FastAPI app with the same routers as production
    test_app = FastAPI(
        title="LLM Chatbot Backend (Test)",
        version="1.0.0-test",
        lifespan=mock_lifespan,
    )
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    test_app.include_router(health_router.router)
    test_app.include_router(chat_router.router)

    with TestClient(test_app, raise_server_exceptions=False) as client:
        yield client
