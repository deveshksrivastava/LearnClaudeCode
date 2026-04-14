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
