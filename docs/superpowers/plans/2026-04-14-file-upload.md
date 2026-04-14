# File Upload Feature — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add multi-file upload, document listing, and file deletion to the ShopFast Assistant page, with immediate ChromaDB re-indexing and LangGraph graph rebuild after every change.

**Architecture:** Three new FastAPI endpoints (`POST /upload`, `GET /documents`, `DELETE /documents/{filename}`) are added to `chat_router.py`. Each mutating endpoint saves/removes files in `data/sample_docs/`, clears ChromaDB, re-indexes all remaining files, and rebuilds `app.state.vector_index` and `app.state.compiled_graph` so the chatbot reflects the change immediately. The frontend adds three typed service functions to `chatbotApi.ts` and a collapsible documents panel (open by default) to `ChatbotPage.tsx`.

**Tech Stack:** Python 3.11, FastAPI `UploadFile`/`File`, Pydantic v2, ChromaDB, LlamaIndex, LangGraph, React 18, TypeScript

---

## File Map

| File | Change |
|------|--------|
| `llm-chatbot-backend/app/models.py` | Add `UploadResponse`, `DocumentListResponse`, `DeleteDocumentResponse` |
| `llm-chatbot-backend/app/api/chat_router.py` | Add `DOCS_DIR` constant, `_rebuild_graph` helper, three new endpoints |
| `llm-chatbot-backend/tests/test_upload_router.py` | New — tests for all three endpoints |
| `llm-chatbot-backend/tests/test_config.py` | Fix pre-existing `rag_top_k` assertion bug (`3` → `6`) |
| `frontend/src/api/chatbotApi.ts` | Add three TypeScript interfaces and three service functions |
| `frontend/src/pages/ChatbotPage.tsx` | Add collapsible documents panel |

---

## Task 1: Fix pre-existing test assertion bug

**Files:**
- Modify: `llm-chatbot-backend/tests/test_config.py:32`

This test currently fails because it asserts `rag_top_k == 3` but the actual default in `config.py` is `6`. Fix it before adding new tests so the test suite is green from the start.

- [ ] **Step 1: Fix the assertion**

In `llm-chatbot-backend/tests/test_config.py`, line 32, change:

```python
        assert settings.rag_top_k == 3
```

to:

```python
        assert settings.rag_top_k == 6
```

- [ ] **Step 2: Verify the test suite passes**

```bash
cd llm-chatbot-backend
.venv/Scripts/python.exe -m pytest tests/ -v
```

Expected: all tests PASS (no failures)

- [ ] **Step 3: Commit**

```bash
git add llm-chatbot-backend/tests/test_config.py
git commit -m "fix: correct rag_top_k default assertion in test_config (3 → 6)"
```

---

## Task 2: Add Pydantic response models

**Files:**
- Modify: `llm-chatbot-backend/app/models.py`

- [ ] **Step 1: Append three models to models.py**

At the bottom of `llm-chatbot-backend/app/models.py`, after the `ErrorResponse` class, append:

```python
# ── /api/v1/upload ───────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    """Response body for POST /api/v1/upload."""
    uploaded: list[str] = Field(description="Filenames that were saved to disk")
    indexed: int = Field(description="Total document chunks now indexed in ChromaDB")
    message: str = Field(description="Human-readable result message")


# ── /api/v1/documents ────────────────────────────────────────────────────────

class DocumentListResponse(BaseModel):
    """Response body for GET /api/v1/documents."""
    documents: list[str] = Field(
        default_factory=list,
        description="Filenames currently in data/sample_docs/",
    )


# ── /api/v1/documents/{filename} ─────────────────────────────────────────────

class DeleteDocumentResponse(BaseModel):
    """Response body for DELETE /api/v1/documents/{filename}."""
    filename: str = Field(description="The deleted filename")
    indexed: int = Field(description="Total document chunks indexed after deletion")
    message: str = Field(description="Human-readable result message")
```

- [ ] **Step 2: Verify models import cleanly**

```bash
cd llm-chatbot-backend
.venv/Scripts/python.exe -c "from app.models import UploadResponse, DocumentListResponse, DeleteDocumentResponse; print('OK')"
```

Expected output: `OK`

- [ ] **Step 3: Commit**

```bash
git add llm-chatbot-backend/app/models.py
git commit -m "feat: add UploadResponse, DocumentListResponse, DeleteDocumentResponse models"
```

---

## Task 3: Add GET /api/v1/documents endpoint

**Files:**
- Modify: `llm-chatbot-backend/app/api/chat_router.py`
- Create: `llm-chatbot-backend/tests/test_upload_router.py`

- [ ] **Step 1: Write the failing tests**

Create `llm-chatbot-backend/tests/test_upload_router.py` with this content:

```python
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
```

- [ ] **Step 2: Run to confirm they fail**

```bash
cd llm-chatbot-backend
.venv/Scripts/python.exe -m pytest tests/test_upload_router.py -v
```

Expected: `AttributeError: module 'app.api.chat_router' has no attribute 'DOCS_DIR'`

- [ ] **Step 3: Update imports, add DOCS_DIR constant, and add the endpoint to chat_router.py**

Replace the entire import block at the top of `llm-chatbot-backend/app/api/chat_router.py` with:

```python
import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from app.models import (
    ChatRequest, ChatResponse,
    IndexRequest, IndexResponse,
    UploadResponse, DocumentListResponse, DeleteDocumentResponse,
)
from app.config import Settings, get_settings
from app.graph.graph_builder import run_conversation_graph, build_conversation_graph
from app.rag.document_loader import load_documents_from_directory, SUPPORTED_EXTENSIONS
from app.rag.vector_store import build_vector_store_index
```

Then, immediately after the `_session_store` line (line ~26), add:

```python
# Path to the directory where uploaded documents are stored.
# Defined at module level so tests can monkeypatch it.
DOCS_DIR = Path(__file__).parent.parent.parent / "data" / "sample_docs"
```

Then append the `list_documents` endpoint after the existing `/index` endpoint:

```python
@router.get(
    "/documents",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List indexed documents",
    description="Returns the filenames of all supported files currently in data/sample_docs/.",
)
async def list_documents(
    settings: Settings = Depends(get_settings),
) -> DocumentListResponse:
    if not DOCS_DIR.exists():
        return DocumentListResponse(documents=[])
    files = sorted(
        f.name for f in DOCS_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    return DocumentListResponse(documents=files)
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd llm-chatbot-backend
.venv/Scripts/python.exe -m pytest tests/test_upload_router.py -v
```

Expected: `test_list_documents_empty` PASS, `test_list_documents_returns_supported_files_sorted` PASS

- [ ] **Step 5: Commit**

```bash
git add llm-chatbot-backend/app/api/chat_router.py llm-chatbot-backend/tests/test_upload_router.py
git commit -m "feat: add GET /api/v1/documents endpoint"
```

---

## Task 4: Add _rebuild_graph helper + POST /api/v1/upload endpoint

**Files:**
- Modify: `llm-chatbot-backend/app/api/chat_router.py`
- Modify: `llm-chatbot-backend/tests/test_upload_router.py`

- [ ] **Step 1: Add upload tests to test_upload_router.py**

Append these tests to `llm-chatbot-backend/tests/test_upload_router.py`:

```python
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
```

- [ ] **Step 2: Run to confirm they fail**

```bash
cd llm-chatbot-backend
.venv/Scripts/python.exe -m pytest tests/test_upload_router.py::test_upload_rejects_unsupported_extension tests/test_upload_router.py::test_upload_saves_file_and_returns_response -v
```

Expected: FAIL with 404 (endpoint does not exist yet)

- [ ] **Step 3: Add _rebuild_graph and upload_documents to chat_router.py**

Insert the `_rebuild_graph` helper immediately before the `list_documents` function:

```python
async def _rebuild_graph(request: Request, settings: Settings) -> int:
    """
    Clear ChromaDB, re-index all files currently in DOCS_DIR, then rebuild
    app.state.vector_index and app.state.compiled_graph.

    WHY REBUILD THE GRAPH?
      The existing /index endpoint only writes to ChromaDB but does not update
      app.state. Without rebuilding, the chatbot keeps using the old index and
      will not see newly uploaded or deleted files.

    Returns:
        int: Total document chunks now indexed in ChromaDB.
    """
    collection = request.app.state.chroma_collection

    # Wipe existing ChromaDB entries without dropping the collection object
    if collection.count() > 0:
        all_ids = collection.get()["ids"]
        if all_ids:
            collection.delete(ids=all_ids)

    # Re-index whatever supported files remain on disk
    indexed_count = 0
    if DOCS_DIR.exists():
        supported = [
            f for f in DOCS_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        if supported:
            indexed_count = load_documents_from_directory(str(DOCS_DIR), collection, settings)

    # Rebuild LlamaIndex VectorStoreIndex from the updated ChromaDB collection
    new_index = build_vector_store_index(collection)
    request.app.state.vector_index = new_index

    # Rebuild LangGraph conversation graph so it uses the new index
    new_graph = build_conversation_graph(
        llm=request.app.state.llm,
        index=new_index,
        settings=settings,
        tools=request.app.state.tools,
    )
    request.app.state.compiled_graph = new_graph

    return indexed_count
```

Then append the `upload_documents` endpoint after `list_documents`:

```python
@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload documents for RAG",
    description=(
        "Upload one or more .txt, .pdf, or .md files. "
        "Files are saved to data/sample_docs/ and ChromaDB is re-indexed immediately."
    ),
)
async def upload_documents(
    request: Request,
    files: List[UploadFile] = File(...),
    settings: Settings = Depends(get_settings),
) -> UploadResponse:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    uploaded_names: list[str] = []
    for upload in files:
        filename = upload.filename or ""

        # Reject path traversal and directory separators in the filename
        if "/" in filename or "\\" in filename or ".." in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid filename: '{filename}'",
            )

        # Reject unsupported extensions
        suffix = Path(filename).suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unsupported file type '{suffix}'. "
                    f"Only {', '.join(sorted(SUPPORTED_EXTENSIONS))} are supported."
                ),
            )

        content = await upload.read()
        dest = DOCS_DIR / filename
        dest.write_bytes(content)
        uploaded_names.append(filename)
        logger.info(f"Saved uploaded file: {dest}")

    indexed_count = await _rebuild_graph(request, settings)

    return UploadResponse(
        uploaded=uploaded_names,
        indexed=indexed_count,
        message=(
            f"Uploaded {len(uploaded_names)} file(s). "
            f"Index now contains {indexed_count} chunk(s)."
        ),
    )
```

- [ ] **Step 4: Run all upload tests to confirm they pass**

```bash
cd llm-chatbot-backend
.venv/Scripts/python.exe -m pytest tests/test_upload_router.py -v
```

Expected: all 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add llm-chatbot-backend/app/api/chat_router.py llm-chatbot-backend/tests/test_upload_router.py
git commit -m "feat: add POST /api/v1/upload with immediate re-indexing"
```

---

## Task 5: Add DELETE /api/v1/documents/{filename} endpoint

**Files:**
- Modify: `llm-chatbot-backend/app/api/chat_router.py`
- Modify: `llm-chatbot-backend/tests/test_upload_router.py`

- [ ] **Step 1: Add delete tests to test_upload_router.py**

Append these tests to `llm-chatbot-backend/tests/test_upload_router.py`:

```python
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
```

- [ ] **Step 2: Run to confirm they fail**

```bash
cd llm-chatbot-backend
.venv/Scripts/python.exe -m pytest tests/test_upload_router.py::test_delete_nonexistent_file_returns_404 tests/test_upload_router.py::test_delete_removes_file_and_reindexes -v
```

Expected: FAIL with 404 or 405 (endpoint does not exist yet)

- [ ] **Step 3: Add delete_document endpoint to chat_router.py**

Append after the `upload_documents` function:

```python
@router.delete(
    "/documents/{filename}",
    response_model=DeleteDocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete an indexed document",
    description=(
        "Remove a file from data/sample_docs/ by name. "
        "Re-indexes remaining files and rebuilds the conversation graph."
    ),
)
async def delete_document(
    filename: str,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> DeleteDocumentResponse:
    # Reject path traversal and directory separators
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid filename: '{filename}'",
        )

    target = DOCS_DIR / filename
    if not target.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{filename}' not found.",
        )

    target.unlink()
    logger.info(f"Deleted document: {target}")

    indexed_count = await _rebuild_graph(request, settings)

    return DeleteDocumentResponse(
        filename=filename,
        indexed=indexed_count,
        message=f"Deleted '{filename}'. Index now contains {indexed_count} chunk(s).",
    )
```

- [ ] **Step 4: Run the full backend test suite**

```bash
cd llm-chatbot-backend
.venv/Scripts/python.exe -m pytest tests/ -v
```

Expected: **all tests PASS** — including `test_config.py`, `test_vector_store.py`, and all 9 tests in `test_upload_router.py`

- [ ] **Step 5: Commit**

```bash
git add llm-chatbot-backend/app/api/chat_router.py llm-chatbot-backend/tests/test_upload_router.py
git commit -m "feat: add DELETE /api/v1/documents/{filename} endpoint"
```

---

## Task 6: Frontend — API service functions

**Files:**
- Modify: `frontend/src/api/chatbotApi.ts`

- [ ] **Step 1: Replace chatbotApi.ts with the updated version**

Replace the entire content of `frontend/src/api/chatbotApi.ts`:

```typescript
const CHATBOT_URL = 'http://127.0.0.1:8002';

// ── Shared types ──────────────────────────────────────────────────────────────

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

export interface ChatResponse {
  session_id: string;
  response: string;
  sources: string[];
}

export interface UploadResponse {
  uploaded: string[];
  indexed: number;
  message: string;
}

export interface DocumentListResponse {
  documents: string[];
}

export interface DeleteDocumentResponse {
  filename: string;
  indexed: number;
  message: string;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Generate a unique session ID on the client — no backend call needed. */
export function newSessionId(): string {
  return crypto.randomUUID();
}

async function handleJsonError(res: Response): Promise<never> {
  const body = await res.json().catch(() => ({ detail: res.statusText }));
  throw new Error((body as { detail?: string }).detail ?? `Request failed: ${res.status}`);
}

// ── Chat ──────────────────────────────────────────────────────────────────────

/**
 * Send one message to the chatbot and return the full response.
 * The chatbot backend keeps conversation history server-side by session_id.
 */
export async function sendMessage(
  message: string,
  sessionId: string,
): Promise<ChatResponse> {
  const res = await fetch(`${CHATBOT_URL}/api/v1/chat-llm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  if (!res.ok) return handleJsonError(res);
  return res.json() as Promise<ChatResponse>;
}

// ── Documents ─────────────────────────────────────────────────────────────────

/**
 * Upload one or more .txt, .pdf, or .md files to data/sample_docs/.
 * The backend re-indexes immediately after saving.
 */
export async function uploadFiles(files: FileList): Promise<UploadResponse> {
  const form = new FormData();
  Array.from(files).forEach((file) => form.append('files', file));

  const res = await fetch(`${CHATBOT_URL}/api/v1/upload`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) return handleJsonError(res);
  return res.json() as Promise<UploadResponse>;
}

/**
 * Return the list of filenames currently in data/sample_docs/.
 */
export async function getDocuments(): Promise<DocumentListResponse> {
  const res = await fetch(`${CHATBOT_URL}/api/v1/documents`);
  if (!res.ok) return handleJsonError(res);
  return res.json() as Promise<DocumentListResponse>;
}

/**
 * Delete a file from data/sample_docs/ by name and trigger re-indexing.
 */
export async function deleteDocument(filename: string): Promise<DeleteDocumentResponse> {
  const res = await fetch(
    `${CHATBOT_URL}/api/v1/documents/${encodeURIComponent(filename)}`,
    { method: 'DELETE' },
  );
  if (!res.ok) return handleJsonError(res);
  return res.json() as Promise<DeleteDocumentResponse>;
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend
npx tsc --noEmit
```

Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/api/chatbotApi.ts
git commit -m "feat: add uploadFiles, getDocuments, deleteDocument to chatbotApi"
```

---

## Task 7: Frontend — Collapsible documents panel in ChatbotPage

**Files:**
- Modify: `frontend/src/pages/ChatbotPage.tsx`

- [ ] **Step 1: Replace ChatbotPage.tsx with the full updated version**

Replace the entire content of `frontend/src/pages/ChatbotPage.tsx`:

```tsx
import { useEffect, useRef, useState } from 'react';
import {
  sendMessage,
  newSessionId,
  uploadFiles,
  getDocuments,
  deleteDocument,
  type ChatMessage,
} from '../api/chatbotApi';

const SESSION_KEY = 'chatbot_session_id';

export default function ChatbotPage() {
  // ── Chat state ────────────────────────────────────────────────────────────
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatError, setChatError] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  // ── Documents panel state ─────────────────────────────────────────────────
  const [panelOpen, setPanelOpen] = useState(true);
  const [documents, setDocuments] = useState<string[]>([]);
  const [docError, setDocError] = useState('');
  const [docsBusy, setDocsBusy] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── Session init ──────────────────────────────────────────────────────────
  useEffect(() => {
    const saved = sessionStorage.getItem(SESSION_KEY);
    const id = saved ?? newSessionId();
    if (!saved) sessionStorage.setItem(SESSION_KEY, id);
    setSessionId(id);
  }, []);

  // ── Load document list on mount ───────────────────────────────────────────
  useEffect(() => {
    fetchDocuments();
  }, []);

  // ── Auto-scroll ───────────────────────────────────────────────────────────
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // ── Document helpers ──────────────────────────────────────────────────────
  async function fetchDocuments() {
    try {
      const data = await getDocuments();
      setDocuments(data.documents);
      setDocError('');
    } catch (err) {
      setDocError(err instanceof Error ? err.message : 'Failed to load documents.');
    }
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    setDocsBusy(true);
    setDocError('');
    try {
      await uploadFiles(files);
      await fetchDocuments();
    } catch (err) {
      setDocError(err instanceof Error ? err.message : 'Upload failed.');
    } finally {
      setDocsBusy(false);
      // Reset so the same file can be re-uploaded if needed
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  }

  async function handleDelete(filename: string) {
    setDocsBusy(true);
    setDocError('');
    try {
      await deleteDocument(filename);
      await fetchDocuments();
    } catch (err) {
      setDocError(err instanceof Error ? err.message : 'Delete failed.');
    } finally {
      setDocsBusy(false);
    }
  }

  // ── Chat helpers ──────────────────────────────────────────────────────────
  async function send() {
    const text = input.trim();
    if (!text || loading || !sessionId) return;
    setInput('');
    setChatError('');
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setLoading(true);
    try {
      const data = await sendMessage(text, sessionId);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response, sources: data.sources },
      ]);
    } catch (err) {
      setChatError(err instanceof Error ? err.message : 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  }

  function startNewConversation() {
    const id = newSessionId();
    sessionStorage.setItem(SESSION_KEY, id);
    setSessionId(id);
    setMessages([]);
    setChatError('');
  }

  function handleKey(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="page chat-page" style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>

      {/* ── Main chat column ──────────────────────────────────────────────── */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div className="chat-header">
          <h1 className="page-title" style={{ marginBottom: 0 }}>ShopFast Assistant</h1>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className="chat-clear-btn"
              onClick={() => setPanelOpen((o) => !o)}
              title={panelOpen ? 'Hide document panel' : 'Show document panel'}
            >
              {panelOpen ? '◀ Docs' : '▶ Docs'}
            </button>
            <button className="chat-clear-btn" onClick={startNewConversation} disabled={loading}>
              New conversation
            </button>
          </div>
        </div>

        <div className="chat-window">
          {messages.length === 0 && !loading && (
            <div className="chat-empty">
              Ask me anything about our products — pricing, stock, recommendations!
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble chat-bubble--${msg.role}`}>
              <span className="chat-role">{msg.role === 'user' ? 'You' : 'Assistant'}</span>
              <p className="chat-content">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <p className="chat-sources">Sources: {msg.sources.join(', ')}</p>
              )}
            </div>
          ))}

          {loading && (
            <div className="chat-bubble chat-bubble--assistant">
              <span className="chat-role">Assistant</span>
              <p className="chat-content chat-thinking">
                <span className="chat-dot" />
                <span className="chat-dot" />
                <span className="chat-dot" />
              </p>
            </div>
          )}

          {chatError && <p className="status-msg error">Error: {chatError}</p>}
          <div ref={bottomRef} />
        </div>

        <div className="chat-input-row">
          <textarea
            className="chat-textarea"
            rows={2}
            placeholder="Ask about products, prices, availability…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            disabled={loading}
          />
          <button
            className="chat-send-btn"
            onClick={send}
            disabled={loading || !input.trim()}
          >
            {loading ? '…' : 'Send'}
          </button>
        </div>
      </div>

      {/* ── Documents panel ───────────────────────────────────────────────── */}
      {panelOpen && (
        <div
          style={{
            width: '220px',
            flexShrink: 0,
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            padding: '1rem',
            background: '#f8fafc',
            alignSelf: 'flex-start',
            position: 'sticky',
            top: '1rem',
          }}
        >
          <h2 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.75rem', margin: '0 0 0.75rem' }}>
            Documents
          </h2>

          {/* Hidden file input — triggered by the button below */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".txt,.pdf,.md"
            style={{ display: 'none' }}
            onChange={handleUpload}
          />

          <button
            className="chat-send-btn"
            style={{ width: '100%', marginBottom: '0.75rem' }}
            disabled={docsBusy}
            onClick={() => fileInputRef.current?.click()}
          >
            {docsBusy ? 'Indexing…' : '+ Upload Files'}
          </button>

          {docError && (
            <p style={{ color: '#e53e3e', fontSize: '0.75rem', marginBottom: '0.5rem', margin: '0 0 0.5rem' }}>
              {docError}
            </p>
          )}

          {documents.length === 0 ? (
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: 0 }}>
              No documents uploaded yet.
            </p>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {documents.map((doc) => (
                <li
                  key={doc}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '0.3rem 0',
                    borderBottom: '1px solid #e2e8f0',
                    fontSize: '0.8rem',
                    gap: '4px',
                  }}
                >
                  <span
                    title={doc}
                    style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', minWidth: 0 }}
                  >
                    {doc}
                  </span>
                  <button
                    onClick={() => handleDelete(doc)}
                    disabled={docsBusy}
                    title={`Delete ${doc}`}
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: docsBusy ? 'not-allowed' : 'pointer',
                      color: '#e53e3e',
                      fontWeight: 'bold',
                      padding: '0 2px',
                      flexShrink: 0,
                      lineHeight: 1,
                    }}
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend
npx tsc --noEmit
```

Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/ChatbotPage.tsx
git commit -m "feat: add collapsible documents panel to ShopFast Assistant page"
```

---

## Task 8: Manual smoke test

With all three services running (`npm run dev` from the project root):

- [ ] **Step 1: Open the ShopFast Assistant page**

Navigate to `http://localhost:5173` and go to the ShopFast Assistant page.

Expected: the Documents panel is visible on the right side showing `example.txt`, `gpt.txt`, `nova.txt`

- [ ] **Step 2: Upload a new .txt file**

Click "+ Upload Files", select any `.txt` file from your machine. Wait for "Indexing…" to resolve.

Expected: the new file appears in the document list; button re-enables

- [ ] **Step 3: Chat about the uploaded file**

Type a question related to the content you just uploaded.

Expected: the assistant responds using that content and lists the file under Sources

- [ ] **Step 4: Delete the file**

Click ✕ next to the file you just uploaded.

Expected: file disappears from the list; button re-enables

- [ ] **Step 5: Try uploading an unsupported file type**

Click "+ Upload Files", select a `.docx` or `.zip` file.

Expected: inline error in the panel (not a page crash); upload button re-enables

- [ ] **Step 6: Toggle the panel**

Click "◀ Docs" to collapse the panel, then "▶ Docs" to re-open it.

Expected: chat area expands to fill the space when closed; panel reappears with the same file list

- [ ] **Step 7: Final commit**

```bash
git add .
git status   # confirm only expected files are staged
git commit -m "feat: complete file upload feature — upload, list, delete with immediate re-indexing"
```
