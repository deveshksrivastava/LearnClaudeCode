# File Upload Feature — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `POST /api/v1/upload` endpoint that accepts a file, saves it, indexes it into ChromaDB, and refreshes the live RAG index.

**Architecture:** A multipart upload endpoint in the existing `chat_router.py` saves the file to `data/sample_docs/`, calls a new `load_single_file()` helper in `document_loader.py`, then rebuilds `app.state.vector_index` so `/chat-llm` immediately sees the new document.

**Tech Stack:** FastAPI `UploadFile`, LlamaIndex `SimpleDirectoryReader(input_files=[...])`, ChromaDB `PersistentClient`, existing `build_vector_store_index()`.

---

## Files that change

| File | Change |
|---|---|
| `app/models.py` | Add `UploadResponse` Pydantic model |
| `app/rag/document_loader.py` | Add `load_single_file(file_path, collection, settings)` |
| `app/api/chat_router.py` | Add `POST /api/v1/upload` endpoint |
| `tests/test_chat_api.py` | Add `TestUploadEndpoint` class |
| `tests/conftest.py` | Add temp-file upload fixtures |

No new files. Everything extends the existing structure.

---

## Likely Failure Points

1. **`app.state.vector_index` not refreshed** — After upload, `request.app.state.vector_index` must be reassigned (not a local variable). If you assign to a local, uploads succeed but never appear in `/chat-llm` RAG results.

2. **Duplicate filenames silently re-index** — Uploading `nova.txt` when it already exists in `data/sample_docs/` overwrites and re-indexes without error. Behaviour is surprising but not a crash. Document it in the response message.

3. **No file size limit by default** — FastAPI/uvicorn don't cap `UploadFile` size. A large PDF can OOM the server during embedding. Add a byte-count check (e.g. 10 MB max) after reading.

4. **Windows path backslash mixing** — `SimpleDirectoryReader(input_files=[path])` can silently skip files if the path mixes separators and LlamaIndex can't detect the extension. Always pass `Path(save_path).resolve()`.

5. **`configure_llama_settings` global race** — It reassigns `LlamaSettings.embed_model` (a global singleton). Concurrent uploads race on it. Not a problem for the current single-worker setup, but worth knowing.

6. **Test fixture already covers upload** — `test_client` in `conftest.py` includes `chat_router`, so no fixture change is needed as long as the upload endpoint stays in `chat_router.py`.

---

## Task 1 — Add `UploadResponse` model

**Files:**
- Modify: `app/models.py`

- [x] **Step 1: Add the model to `models.py`** after the `IndexResponse` class

```python
class UploadResponse(BaseModel):
    """
    Response body for POST /api/v1/upload.

    Fields:
        filename:       Original name of the uploaded file.
        indexed_chunks: Number of text chunks stored in ChromaDB.
        message:        Human-readable summary.
    """
    filename: str = Field(description="Name of the uploaded file")
    indexed_chunks: int = Field(description="Number of document chunks stored in ChromaDB")
    message: str = Field(description="Human-readable result message")
```

- [x] **Step 2: Verify import works**

```bash
cd llm-chatbot-backend
venv/Scripts/python.exe -c "from app.models import UploadResponse; print('OK')"
```

Expected: `OK`

- [x] **Step 3: Commit**

```bash
git add app/models.py
git commit -m "feat: add UploadResponse model"
```

---

## Task 2 — Add `load_single_file()` to document_loader

**Files:**
- Modify: `app/rag/document_loader.py`
- Test: `tests/test_chat_api.py` (temporary — move to dedicated file if preferred)

- [x] **Step 1: Write the failing test** in `tests/test_chat_api.py`

```python
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.rag.document_loader import load_single_file
from app.config import Settings


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
        from app.rag.document_loader import load_single_file
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
```

- [x] **Step 2: Run tests to confirm they fail**

```bash
cd llm-chatbot-backend
venv/Scripts/python.exe -m pytest tests/test_chat_api.py::TestLoadSingleFile -v
```

Expected: `ImportError` or `AttributeError` — `load_single_file` does not exist yet.

- [x] **Step 3: Implement `load_single_file()` in `document_loader.py`**

Add after the existing `load_documents_from_directory` function:

```python
def load_single_file(
    file_path: str,
    collection: chromadb.Collection,
    settings: Settings,
) -> int:
    """
    Loads a single file into ChromaDB via LlamaIndex.

    Uses SimpleDirectoryReader(input_files=[...]) so only this one file
    is processed — not the whole directory.

    Args:
        file_path:  Absolute or relative path to the file.
        collection: ChromaDB collection to store embeddings in.
        settings:   Application settings (embedding model + chunking).

    Returns:
        int: Number of document chunks stored in ChromaDB.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError:        If the file extension is not supported.
        Exception:         For LlamaIndex/ChromaDB errors.
    """
    path = Path(file_path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{path.suffix}'. "
            f"Allowed: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    logger.info(f"Indexing single file: {path.name}")

    try:
        configure_llama_settings(settings)

        reader = SimpleDirectoryReader(input_files=[str(path)])
        documents = reader.load_data()
        logger.info(f"Loaded {len(documents)} document(s) from {path.name}")

        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=False,
        )

        logger.info(f"Indexed {len(documents)} chunk(s) from {path.name}")
        return len(documents)

    except (FileNotFoundError, ValueError):
        raise
    except Exception as e:
        logger.error(f"Failed to index file '{file_path}': {e}")
        raise
```

- [x] **Step 4: Run tests — expect pass**

```bash
venv/Scripts/python.exe -m pytest tests/test_chat_api.py::TestLoadSingleFile -v
```

Expected: all 3 tests `PASSED`.

- [x] **Step 5: Commit**

```bash
git add app/rag/document_loader.py tests/test_chat_api.py
git commit -m "feat: add load_single_file() for per-file RAG indexing"
```

---

## Task 3 — Add `POST /api/v1/upload` endpoint

**Files:**
- Modify: `app/api/chat_router.py`
- Modify: `tests/test_chat_api.py`

- [x] **Step 1: Write the failing tests**

Add `TestUploadEndpoint` to `tests/test_chat_api.py`:

```python
class TestUploadEndpoint:
    """Tests for POST /api/v1/upload."""

    def test_upload_valid_txt_returns_200(self, test_client):
        """A valid .txt file upload returns HTTP 200."""
        file_content = b"This is a test document for upload."
        response = test_client.post(
            "/api/v1/upload",
            files={"file": ("test.txt", file_content, "text/plain")},
        )
        assert response.status_code == 200

    def test_upload_response_has_required_fields(self, test_client):
        """Upload response contains filename, indexed_chunks, message."""
        file_content = b"Sample content for upload test."
        response = test_client.post(
            "/api/v1/upload",
            files={"file": ("sample.txt", file_content, "text/plain")},
        )
        data = response.json()
        assert "filename" in data
        assert "indexed_chunks" in data
        assert "message" in data

    def test_upload_returns_400_for_unsupported_extension(self, test_client):
        """Uploading an .exe returns HTTP 400."""
        response = test_client.post(
            "/api/v1/upload",
            files={"file": ("malware.exe", b"bad content", "application/octet-stream")},
        )
        assert response.status_code == 400

    def test_upload_returns_400_if_no_file_provided(self, test_client):
        """Omitting the file field returns HTTP 422."""
        response = test_client.post("/api/v1/upload")
        assert response.status_code == 422

    def test_upload_returns_400_for_oversized_file(self, test_client):
        """A file over 10 MB returns HTTP 400."""
        big_content = b"x" * (10 * 1024 * 1024 + 1)  # 10 MB + 1 byte
        response = test_client.post(
            "/api/v1/upload",
            files={"file": ("big.txt", big_content, "text/plain")},
        )
        assert response.status_code == 400
```

- [x] **Step 2: Run tests to confirm they fail**

```bash
venv/Scripts/python.exe -m pytest tests/test_chat_api.py::TestUploadEndpoint -v
```

Expected: `404 Not Found` — endpoint doesn't exist yet.

- [x] **Step 3: Add the upload endpoint to `chat_router.py`**

Add these imports at the top of `chat_router.py`:

```python
import shutil
from pathlib import Path
from fastapi import File, UploadFile
from app.models import ChatRequest, ChatResponse, IndexRequest, IndexResponse, UploadResponse
from app.rag.document_loader import load_documents_from_directory, load_single_file
from app.rag.vector_store import build_vector_store_index
```

Add the endpoint after `index_documents`:

```python
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

UPLOAD_DIR = Path(__file__).parent.parent.parent / "data" / "sample_docs"


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and index a document",
    description=(
        "Upload a .txt, .pdf, or .md file. The file is saved to the sample_docs "
        "folder and immediately indexed into ChromaDB for RAG retrieval."
    ),
)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> UploadResponse:
    """
    POST /api/v1/upload — file upload and indexing endpoint.

    WHAT THIS DOES:
      1. Validates file extension and size
      2. Saves the file to data/sample_docs/
      3. Indexes it into ChromaDB via load_single_file()
      4. Rebuilds app.state.vector_index so /chat-llm sees it immediately
      5. Returns filename + chunk count

    Args:
        request:  FastAPI Request (used to access app.state).
        file:     The uploaded file (multipart/form-data).
        settings: Application settings.

    Returns:
        UploadResponse: Filename, number of indexed chunks, and status message.

    Raises:
        HTTPException 400: Bad extension, oversized file, or indexing error.
        HTTPException 503: If ChromaDB is not ready.
    """
    filename = file.filename or "upload"
    extension = Path(filename).suffix.lower()
    allowed = {".txt", ".pdf", ".md"}

    if extension not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{extension}'. Allowed: {', '.join(sorted(allowed))}",
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large ({len(content)} bytes). Maximum allowed: {MAX_UPLOAD_BYTES} bytes.",
        )

    chroma_client = getattr(request.app.state, "chroma_client", None)
    if chroma_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ChromaDB is not ready. Check server logs.",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path = UPLOAD_DIR / filename

    try:
        save_path.write_bytes(content)
        logger.info(f"Saved uploaded file: {save_path}")

        collection = chroma_client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        request.app.state.chroma_collection = collection

        indexed_chunks = load_single_file(
            file_path=str(save_path.resolve()),
            collection=collection,
            settings=settings,
        )

        # Rebuild the live index so /chat-llm immediately sees the new document
        request.app.state.vector_index = build_vector_store_index(collection)

    except HTTPException:
        raise
    except ValueError as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        save_path.unlink(missing_ok=True)
        logger.error(f"Upload failed for '{filename}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )

    return UploadResponse(
        filename=filename,
        indexed_chunks=indexed_chunks,
        message=f"'{filename}' uploaded and indexed as {indexed_chunks} chunk(s). "
                f"Note: uploading a file with the same name as an existing file will replace it.",
    )
```

- [x] **Step 4: Run all tests**

```bash
venv/Scripts/python.exe -m pytest tests/ -v
```

Expected: all existing tests still pass; all 4 `TestUploadEndpoint` tests pass.

- [x] **Step 5: Manual smoke test against the running server**

```bash
curl -X POST http://localhost:8002/api/v1/upload \
  -F "file=@data/sample_docs/nova.txt"
```

Expected response shape:
```json
{
  "filename": "nova.txt",
  "indexed_chunks": 3,
  "message": "'nova.txt' uploaded and indexed as 3 chunk(s)..."
}
```

- [x] **Step 6: Commit**

```bash
git add app/api/chat_router.py app/models.py tests/test_chat_api.py
git commit -m "feat: add POST /api/v1/upload endpoint with file validation and RAG re-index"
```

---

## Self-review checklist

- [x] `UploadResponse` model defined before it is used in the endpoint
- [x] `load_single_file` import added to `chat_router.py`
- [x] `build_vector_store_index` import added to `chat_router.py`
- [x] `UploadResponse` import added to `chat_router.py`
- [x] File size check happens before disk write (no partial saves)
- [x] Cleanup (`save_path.unlink`) on both `ValueError` and generic `Exception`
- [x] `app.state.vector_index` reassigned on `request.app.state` (not a local)
- [x] Extension check uses `.lower()` — handles `.TXT`, `.PDF`
- [x] `UPLOAD_DIR.mkdir(parents=True, exist_ok=True)` — safe on first run
- [x] Test for oversized file checks > 10 MB + 1 byte (boundary condition)
- [x] No placeholder steps — all code shown in full
