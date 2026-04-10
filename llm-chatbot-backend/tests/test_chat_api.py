# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# Integration tests for the FastAPI endpoints: /chat, /health, /index.
# These tests use FastAPI's TestClient to make real HTTP requests against the
# app — without starting an actual server or calling real external services.
# ─────────────────────────────────────────────────────────────────────────────

import pytest
from unittest.mock import MagicMock, patch


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
    """Tests for POST /api/v1/chat."""

    def test_chat_returns_200_with_valid_request(self, test_client):
        """
        WHAT: Tests that a valid chat request returns HTTP 200.
        WHY:  This is the main success path — the most important test.
        """
        response = test_client.post(
            "/api/v1/chat",
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
            "/api/v1/chat",
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
            "/api/v1/chat",
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
            "/api/v1/chat",
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
            "/api/v1/chat",
            json={"message": "Hello there"},  # 'session_id' is missing
        )
        assert response.status_code == 422

    def test_chat_returns_422_for_empty_message(self, test_client):
        """
        WHAT: Tests that an empty message string returns HTTP 422.
        WHY:  The Pydantic model has min_length=1, so empty strings are invalid.
        """
        response = test_client.post(
            "/api/v1/chat",
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
            "/api/v1/chat",
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
