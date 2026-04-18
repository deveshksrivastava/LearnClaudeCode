# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# Integration tests for the FastAPI endpoints: /chat, /health, /index.
# These tests use FastAPI's TestClient to make real HTTP requests against the
# app — without starting an actual server or calling real external services.
# ─────────────────────────────────────────────────────────────────────────────

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.rag.document_loader import load_single_file
from app.config import Settings
from app.models import DocumentInfo, DocumentListResponse


class TestHealthEndpoint:
    """Tests for GET /api/v1/health."""

    def test_health_returns_200(self, test_client):
        """
        WHAT: Tests that the health endpoint returns HTTP 200.
        WHY:  Azure Container Apps uses this endpoint to decide if the container
              is alive. A non-200 response triggers a restart.
        """
        response = test_client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_returns_status_ok(self, test_client):
        """
        WHAT: Tests that the health response body contains {"status": "ok"}.
        WHY:  The health check contract requires this specific response shape.
              Load balancers may parse this field.
        """
        response = test_client.get("/api/v1/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_version(self, test_client):
        """
        WHAT: Tests that the health response includes the app version.
        WHY:  Version in health response helps with deployment troubleshooting —
              you can verify which version is actually running on Azure.
        """
        response = test_client.get("/api/v1/health")
        data = response.json()
        assert "version" in data
        assert len(data["version"]) > 0


class TestChatEndpoint:
    """Tests for POST /api/v1/chat-llm."""

    def test_chat_returns_200_with_valid_request(self, test_client):
        """
        WHAT: Tests that a valid chat request returns HTTP 200.
        WHY:  This is the main success path — the most important test.
        """
        response = test_client.post(
            "/api/v1/chat-llm",
            json={
                "session_id": "test-session-001",
                "message": "Hello, how are you?",
            },
        )
        assert response.status_code == 200

    def test_chat_response_has_required_fields(self, test_client):
        """
        WHAT: Tests that the response body contains all required fields.
        WHY:  The frontend depends on 'session_id', 'response', and 'sources'
              being present. Missing fields would break the frontend.
        """
        response = test_client.post(
            "/api/v1/chat-llm",
            json={
                "session_id": "test-session-002",
                "message": "What is the refund policy?",
            },
        )
        data = response.json()
        assert "session_id" in data
        assert "response" in data
        assert "sources" in data

    def test_chat_echoes_session_id(self, test_client):
        """
        WHAT: Tests that the response echoes back the same session_id.
        WHY:  The frontend uses session_id to route responses to the right
              conversation thread. Returning a different ID would be a bug.
        """
        session_id = "my-specific-session-xyz"
        response = test_client.post(
            "/api/v1/chat-llm",
            json={"session_id": session_id, "message": "Hello"},
        )
        data = response.json()
        assert data["session_id"] == session_id

    def test_chat_returns_422_for_missing_message(self, test_client):
        """
        WHAT: Tests that a missing 'message' field returns HTTP 422 (Unprocessable Entity).
        WHY:  Pydantic validates the request body. Missing required fields should
              return a 422, not a 500 internal server error.
        """
        response = test_client.post(
            "/api/v1/chat-llm",
            json={"session_id": "test-session"},  # 'message' is missing
        )
        assert response.status_code == 422

    def test_chat_returns_422_for_missing_session_id(self, test_client):
        """
        WHAT: Tests that a missing 'session_id' field returns HTTP 422.
        WHY:  session_id is required to maintain conversation context.
              The API must reject requests without it.
        """
        response = test_client.post(
            "/api/v1/chat-llm",
            json={"message": "Hello there"},  # 'session_id' is missing
        )
        assert response.status_code == 422

    def test_chat_returns_422_for_empty_message(self, test_client):
        """
        WHAT: Tests that an empty message string returns HTTP 422.
        WHY:  The Pydantic model has min_length=1, so empty strings are invalid.
        """
        response = test_client.post(
            "/api/v1/chat-llm",
            json={"session_id": "test", "message": ""},
        )
        assert response.status_code == 422

    def test_chat_returns_503_when_graph_not_ready(self, test_client):
        """
        WHAT: Tests that a 503 is returned if the LangGraph was not initialised.
        WHY:  If startup fails (e.g., bad API key), the graph won't be set.
              We must return 503 (Service Unavailable) not 500, so the load
              balancer knows to route traffic away from this instance.
        """
        # Remove the graph from app state to simulate startup failure
        test_client.app.state.compiled_graph = None

        response = test_client.post(
            "/api/v1/chat-llm",
            json={"session_id": "test", "message": "Hello"},
        )
        assert response.status_code == 503

        # Restore for other tests
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {
            "session_id": "test",
            "messages": [],
            "user_input": "Hello",
            "retrieved_context": "",
            "sources": [],
            "final_response": "Hello back!",
            "error": None,
        }
        test_client.app.state.compiled_graph = mock_graph


class TestIndexEndpoint:
    """Tests for POST /api/v1/index."""

    def test_index_returns_400_for_nonexistent_directory(self, test_client):
        """
        WHAT: Tests that a 400 is returned when the directory doesn't exist.
        WHY:  The client must be told their input is wrong (400 Bad Request)
              not that the server broke (500 Internal Server Error).
        """
        response = test_client.post(
            "/api/v1/index",
            json={"directory": "/this/path/definitely/does/not/exist"},
        )
        assert response.status_code == 400

    def test_index_returns_422_for_missing_directory(self, test_client):
        """
        WHAT: Tests that a missing 'directory' field returns 422.
        WHY:  The Pydantic model requires the directory field.
        """
        response = test_client.post(
            "/api/v1/index",
            json={},  # Missing 'directory'
        )
        assert response.status_code == 422


class TestListDocumentsEndpoint:
    """Tests for GET /api/v1/documents."""

    def test_list_documents_returns_200(self, test_client):
        """GET /api/v1/documents returns HTTP 200."""
        response = test_client.get("/api/v1/documents")
        assert response.status_code == 200

    def test_list_documents_response_has_files_key(self, test_client):
        """Response body contains a 'files' list."""
        response = test_client.get("/api/v1/documents")
        data = response.json()
        assert "files" in data
        assert isinstance(data["files"], list)

    def test_list_documents_returns_empty_when_dir_missing(self, test_client):
        """Returns empty list rather than 500 when UPLOAD_DIR does not exist."""
        with patch("app.api.chat_router.UPLOAD_DIR", Path("/nonexistent/path")):
            response = test_client.get("/api/v1/documents")
        assert response.status_code == 200
        assert response.json()["files"] == []

    def test_list_documents_returns_file_metadata(self, test_client, tmp_path):
        """Each entry has filename, size_bytes, and last_modified."""
        (tmp_path / "hello.txt").write_text("some content")
        with patch("app.api.chat_router.UPLOAD_DIR", tmp_path):
            response = test_client.get("/api/v1/documents")
        data = response.json()
        assert len(data["files"]) == 1
        entry = data["files"][0]
        assert entry["filename"] == "hello.txt"
        assert entry["size_bytes"] > 0
        assert "last_modified" in entry

    def test_list_documents_excludes_unsupported_extensions(self, test_client, tmp_path):
        """Files with unsupported extensions are not included in the list."""
        (tmp_path / "keep.txt").write_text("yes")
        (tmp_path / "ignore.exe").write_text("no")
        with patch("app.api.chat_router.UPLOAD_DIR", tmp_path):
            response = test_client.get("/api/v1/documents")
        filenames = [f["filename"] for f in response.json()["files"]]
        assert "keep.txt" in filenames
        assert "ignore.exe" not in filenames


class TestLoadSingleFile:
    """Unit tests for load_single_file()."""

    def _make_settings(self):
        return Settings(
            llm_provider="openai",
            openai_api_key="sk-test-fake",
            openai_embedding_model="text-embedding-ada-002",
            rag_chunk_size=256,
            rag_chunk_overlap=20,
        )

    def test_load_single_file_returns_chunk_count(self, tmp_path):
        """load_single_file returns a positive integer for a valid .txt file."""
        sample = tmp_path / "sample.txt"
        sample.write_text("Hello world. This is a test document with enough text to chunk.")

        mock_collection = MagicMock()
        settings = self._make_settings()

        with patch("app.rag.document_loader.configure_llama_settings"), \
             patch("app.rag.document_loader.VectorStoreIndex") as mock_index, \
             patch("app.rag.document_loader.ChromaVectorStore"), \
             patch("app.rag.document_loader.StorageContext"):
            mock_index.from_documents.return_value = MagicMock()
            result = load_single_file(str(sample), mock_collection, settings)

        assert isinstance(result, int)
        assert result >= 1

    def test_load_single_file_raises_for_missing_file(self, tmp_path):
        """load_single_file raises FileNotFoundError for a non-existent path."""
        mock_collection = MagicMock()
        settings = self._make_settings()

        with pytest.raises(FileNotFoundError):
            load_single_file(str(tmp_path / "missing.txt"), mock_collection, settings)

    def test_load_single_file_raises_for_unsupported_extension(self, tmp_path):
        """load_single_file raises ValueError for .exe or other unsupported types."""
        bad_file = tmp_path / "virus.exe"
        bad_file.write_text("bad")
        mock_collection = MagicMock()
        settings = self._make_settings()

        with pytest.raises(ValueError, match="Unsupported file type"):
            load_single_file(str(bad_file), mock_collection, settings)


class TestUploadEndpoint:
    """Tests for POST /api/v1/upload."""

    def test_upload_valid_txt_returns_200(self, test_client, tmp_path):
        """A valid .txt file upload returns HTTP 200."""
        file_content = b"This is a test document for upload."
        with patch("app.api.chat_router.load_single_file", return_value=2), \
             patch("app.api.chat_router.build_vector_store_index", return_value=MagicMock()), \
             patch("app.api.chat_router.UPLOAD_DIR", tmp_path):
            response = test_client.post(
                "/api/v1/upload",
                files={"file": ("test.txt", file_content, "text/plain")},
            )
        assert response.status_code == 200

    def test_upload_response_has_required_fields(self, test_client, tmp_path):
        """Upload response contains filename, indexed_chunks, message."""
        file_content = b"Sample content for upload test."
        with patch("app.api.chat_router.load_single_file", return_value=3), \
             patch("app.api.chat_router.build_vector_store_index", return_value=MagicMock()), \
             patch("app.api.chat_router.UPLOAD_DIR", tmp_path):
            response = test_client.post(
                "/api/v1/upload",
                files={"file": ("sample.txt", file_content, "text/plain")},
            )
        data = response.json()
        assert "filename" in data
        assert "indexed_chunks" in data
        assert "message" in data

    def test_upload_returns_400_for_unsupported_extension(self, test_client):
        """Uploading an .exe returns HTTP 400 — rejected before any indexing."""
        response = test_client.post(
            "/api/v1/upload",
            files={"file": ("malware.exe", b"bad content", "application/octet-stream")},
        )
        assert response.status_code == 400

    def test_upload_returns_422_if_no_file_provided(self, test_client):
        """Omitting the file field returns HTTP 422."""
        response = test_client.post("/api/v1/upload")
        assert response.status_code == 422

    def test_upload_returns_400_for_oversized_file(self, test_client):
        """A file over 10 MB returns HTTP 400 — rejected after read, before disk write."""
        big_content = b"x" * (10 * 1024 * 1024 + 1)  # 10 MB + 1 byte
        response = test_client.post(
            "/api/v1/upload",
            files={"file": ("big.txt", big_content, "text/plain")},
        )
        assert response.status_code == 400
