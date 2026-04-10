const CHATBOT_URL = 'http://127.0.0.1:8001';

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
  const res = await fetch(`${CHATBOT_URL}/api/v1/chat`, {
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
