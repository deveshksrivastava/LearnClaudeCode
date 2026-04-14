# ─────────────────────────────────────────────────────────────────────────────
# Tests for upload, document listing, and document deletion endpoints.
# Each test redirects DOCS_DIR to a tmp_path directory so no real files
# are touched during the test run.
# ─────────────────────────────────────────────────────────────────────────────

import pytest
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

import app.api.chat_router as router_module
from app.api.chat_router import router


@pytest.fixture(autouse=True)
def patch_docs_dir(tmp_path):
    """Redirect DOCS_DIR to a temp directory for every test in this file."""
    docs = tmp_path / "sample_docs"
    docs.mkdir()
    original = router_module.DOCS_DIR
    router_module.DOCS_DIR = docs
    yield docs
    router_module.DOCS_DIR = original


@pytest.fixture
def client(patch_docs_dir):
    """TestClient with a minimal FastAPI app and mocked app.state."""
    app = FastAPI()
    app.include_router(router)
    app.state.chroma_client = MagicMock()
    app.state.chroma_collection = MagicMock()
    app.state.chroma_collection.count.return_value = 0
    app.state.chroma_collection.get.return_value = {"ids": []}
    app.state.llm = MagicMock()
    app.state.tools = []
    app.state.compiled_graph = MagicMock()
    app.state.vector_index = None
    return TestClient(app)


# ── GET /api/v1/documents ────────────────────────────────────────────────────

def test_list_documents_empty(client):
    res = client.get("/api/v1/documents")
    assert res.status_code == 200
    assert res.json() == {"documents": []}


def test_list_documents_returns_supported_files_sorted(client, patch_docs_dir):
    (patch_docs_dir / "zebra.txt").write_text("hello")
    (patch_docs_dir / "alpha.pdf").write_bytes(b"%PDF-1.4")
    (patch_docs_dir / "notes.md").write_text("# notes")
    (patch_docs_dir / "ignore.docx").write_bytes(b"docx")
    res = client.get("/api/v1/documents")
    assert res.status_code == 200
    assert res.json()["documents"] == ["alpha.pdf", "notes.md", "zebra.txt"]


# ── POST /api/v1/upload ──────────────────────────────────────────────────────

def test_upload_rejects_unsupported_extension(client):
    res = client.post(
        "/api/v1/upload",
        files=[("files", ("virus.exe", b"MZ", "application/octet-stream"))],
    )
    assert res.status_code == 400
    assert "supported" in res.json()["detail"].lower()


def test_upload_rejects_path_traversal(client):
    res = client.post(
        "/api/v1/upload",
        files=[("files", ("../evil.txt", b"bad", "text/plain"))],
    )
    assert res.status_code == 400


def test_upload_saves_file_and_returns_response(client, patch_docs_dir):
    with patch("app.api.chat_router.load_documents_from_directory", return_value=3), \
         patch("app.api.chat_router.build_vector_store_index", return_value=None), \
         patch("app.api.chat_router.build_conversation_graph", return_value=MagicMock()):
        res = client.post(
            "/api/v1/upload",
            files=[("files", ("policy.txt", b"return policy text", "text/plain"))],
        )
    assert res.status_code == 200
    data = res.json()
    assert data["uploaded"] == ["policy.txt"]
    assert data["indexed"] == 3
    assert "policy.txt" in data["message"]
    assert (patch_docs_dir / "policy.txt").exists()


def test_upload_multiple_files(client, patch_docs_dir):
    with patch("app.api.chat_router.load_documents_from_directory", return_value=4), \
         patch("app.api.chat_router.build_vector_store_index", return_value=None), \
         patch("app.api.chat_router.build_conversation_graph", return_value=MagicMock()):
        res = client.post(
            "/api/v1/upload",
            files=[
                ("files", ("doc1.txt", b"content one", "text/plain")),
                ("files", ("doc2.md", b"# content two", "text/markdown")),
            ],
        )
    assert res.status_code == 200
    data = res.json()
    assert set(data["uploaded"]) == {"doc1.txt", "doc2.md"}
    assert (patch_docs_dir / "doc1.txt").exists()
    assert (patch_docs_dir / "doc2.md").exists()


# ── DELETE /api/v1/documents/{filename} ──────────────────────────────────────

def test_delete_nonexistent_file_returns_404(client):
    res = client.delete("/api/v1/documents/ghost.txt")
    assert res.status_code == 404
    assert "ghost.txt" in res.json()["detail"]


def test_delete_path_traversal_returns_400(client):
    # Filename containing ".." must be rejected before touching disk
    res = client.delete("/api/v1/documents/..evil")
    assert res.status_code == 400


def test_delete_removes_file_and_reindexes(client, patch_docs_dir):
    (patch_docs_dir / "target.txt").write_text("some content")
    with patch("app.api.chat_router.load_documents_from_directory", return_value=0), \
         patch("app.api.chat_router.build_vector_store_index", return_value=None), \
         patch("app.api.chat_router.build_conversation_graph", return_value=MagicMock()):
        res = client.delete("/api/v1/documents/target.txt")
    assert res.status_code == 200
    data = res.json()
    assert data["filename"] == "target.txt"
    assert data["indexed"] == 0
    assert not (patch_docs_dir / "target.txt").exists()
