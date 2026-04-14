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
