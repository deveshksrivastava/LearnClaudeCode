# File Upload Feature — Design Spec

**Date:** 2026-04-14
**Feature:** Multi-file upload on ShopFast Assistant page with immediate RAG re-indexing
**Branch:** feature/llm-langchain-chatboart-azure

---

## Goal

Allow users to upload `.txt` and `.pdf` files directly from the ShopFast Assistant chat page. Uploaded files are saved to `llm-chatbot-backend/data/sample_docs/`, immediately re-indexed into ChromaDB, and the LangGraph conversation graph is rebuilt so the chatbot can answer questions about the new content right away. Users can also view and delete indexed files from the same panel.

---

## Architecture

### Backend — 3 new endpoints (added to `llm-chatbot-backend/app/api/chat_router.py`)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/upload` | Accept `multipart/form-data`, save to `data/sample_docs/`, re-index, rebuild graph |
| `GET` | `/api/v1/documents` | Return list of filenames in `data/sample_docs/` |
| `DELETE` | `/api/v1/documents/{filename}` | Delete named file, re-index remaining files, rebuild graph |

**Critical:** After every upload or delete, the handler must:
1. Clear existing ChromaDB collection entries
2. Re-index all files currently in `data/sample_docs/`
3. Rebuild `app.state.vector_index` (LlamaIndex `VectorStoreIndex`)
4. Rebuild and recompile `app.state.compiled_graph` (LangGraph)

This ensures the chatbot uses new content immediately. The existing `POST /api/v1/index` endpoint does not do steps 3–4 and is not used by this feature.

### New Pydantic models (added to `llm-chatbot-backend/app/models.py`)

```python
class UploadResponse(BaseModel):
    uploaded: list[str]      # filenames that were saved
    indexed: int             # total documents now in ChromaDB
    message: str

class DocumentListResponse(BaseModel):
    documents: list[str]     # filenames currently in data/sample_docs/

class DeleteDocumentResponse(BaseModel):
    filename: str            # the deleted file
    indexed: int             # total documents now in ChromaDB after deletion
    message: str
```

### Supported file types
`.txt` and `.pdf` — enforced by the existing `SUPPORTED_EXTENSIONS` constant in `document_loader.py`. All other types are rejected with `400 Bad Request` before touching disk.

---

## Frontend

### API service layer (`frontend/src/api/chatbotApi.ts`)

Three new functions added alongside the existing `sendMessage`:

```ts
uploadFiles(files: FileList): Promise<UploadResponse>
getDocuments(): Promise<DocumentListResponse>
deleteDocument(filename: string): Promise<DeleteDocumentResponse>
```

All use the existing `CHATBOT_URL` constant. No new HTTP libraries introduced.

### Page layout (`frontend/src/pages/ChatbotPage.tsx`)

```
┌─────────────────────────────────┬──────────────────────┐
│  Chat header + "New conversation"│  [◀ Documents]       │
├─────────────────────────────────┤                      │
│                                 │  [+ Upload Files]    │
│         Chat window             │  ─────────────────   │
│                                 │  example.txt    [✕]  │
│                                 │  gpt.txt        [✕]  │
│                                 │  nova.txt       [✕]  │
├─────────────────────────────────┤                      │
│       Input + Send              │  (Indexing…)         │
└─────────────────────────────────┴──────────────────────┘
```

- Panel is **open by default** (documents are already indexed on startup)
- Toggle button collapses/expands the panel
- "Upload Files" triggers a hidden `<input type="file" multiple accept=".txt,.pdf">` — no third-party library
- File list is fetched on component mount via `getDocuments()`
- File list refreshes after every successful upload or delete

### UI states

| State | Behaviour |
|-------|-----------|
| Uploading / indexing | Spinner in panel; upload button and all delete icons disabled |
| Success | File list refreshes; no toast needed |
| Error | Inline error message in panel; chat area unaffected |
| Empty list | Panel shows "No documents uploaded yet" placeholder |
| No files selected | Upload button disabled until `<input>` has a selection |

---

## Error Handling

### Backend

| Scenario | Response |
|----------|----------|
| Unsupported file type | `400` — `"Only .txt and .pdf files are supported"` |
| Duplicate filename | Overwrite silently, re-index (last-write wins) |
| Delete non-existent file | `404 Not Found` |
| Path traversal in filename (`../`, `/`) | `400` — rejected before touching disk |
| All files deleted | ChromaDB cleared, `vector_index = None`, graph rebuilt without RAG |
| Re-index failure | `500` — files already saved to disk remain (no rollback) |

### Frontend

- Upload with nothing selected → button stays disabled
- Server error → inline error in panel, chat continues to work
- Slow indexing → "Indexing…" state on button until response received

---

## Files Changed

| File | Change |
|------|--------|
| `llm-chatbot-backend/app/models.py` | Add `UploadResponse`, `DocumentListResponse`, `DeleteDocumentResponse` |
| `llm-chatbot-backend/app/api/chat_router.py` | Add `POST /upload`, `GET /documents`, `DELETE /documents/{filename}` |
| `frontend/src/api/chatbotApi.ts` | Add `uploadFiles()`, `getDocuments()`, `deleteDocument()` |
| `frontend/src/pages/ChatbotPage.tsx` | Add collapsible documents panel with upload + file list + delete |

No new dependencies introduced on either side.

---

## Out of Scope

- Authentication / authorization on upload or delete endpoints (noted as a known gap in the contract review — to be addressed separately)
- File size limits (left to OS/FastAPI defaults for now)
- Showing document content previews
- Downloading uploaded files from the frontend
