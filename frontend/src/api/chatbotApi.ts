const CHATBOT_URL = 'http://127.0.0.1:8002';

export interface UploadResponse {
  filename: string;
  indexed_chunks: number;
  message: string;
}

/**
 * Upload a .txt, .pdf, or .md file to the chatbot backend.
 * The file is saved and immediately indexed into ChromaDB.
 */
export async function uploadDocument(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(`${CHATBOT_URL}/api/v1/upload`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((body as { detail?: string }).detail ?? 'Upload failed');
  }

  return res.json() as Promise<UploadResponse>;
}

export interface DocumentInfo {
  filename: string;
  size_bytes: number;
  last_modified: string;
}

/** Fetch the list of uploaded documents from the backend. */
export async function listDocuments(): Promise<DocumentInfo[]> {
  const res = await fetch(`${CHATBOT_URL}/api/v1/documents`);
  if (!res.ok) throw new Error('Failed to load documents');
  const data = await res.json() as { files: DocumentInfo[] };
  return data.files;
}

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

/** Generate a unique session ID on the client — no backend call needed. */
export function newSessionId(): string {
  return crypto.randomUUID();
}

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

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((body as { detail?: string }).detail ?? 'Chat request failed');
  }

  return res.json() as Promise<ChatResponse>;
}
