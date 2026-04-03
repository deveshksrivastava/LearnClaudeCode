const BASE_URL = 'http://127.0.0.1:8000';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  created_at?: string;
}

export async function newChatSession(): Promise<string> {
  const res = await fetch(`${BASE_URL}/chat/session`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to create session');
  const data = await res.json();
  return data.session_id as string;
}

export async function getChatHistory(sessionId: string): Promise<ChatMessage[]> {
  const res = await fetch(`${BASE_URL}/chat/history/${encodeURIComponent(sessionId)}`);
  if (!res.ok) throw new Error('Failed to fetch history');
  return res.json();
}

export async function clearChatHistory(sessionId: string): Promise<void> {
  await fetch(`${BASE_URL}/chat/history/${encodeURIComponent(sessionId)}`, {
    method: 'DELETE',
  });
}

/**
 * Stream a chat response token-by-token.
 * Calls onToken for each streamed token, onDone when complete,
 * and onError on failure.
 */
export async function streamChat(
  message: string,
  sessionId: string,
  onToken: (token: string) => void,
  onDone: (finalSessionId: string) => void,
  onError: (err: string) => void,
): Promise<void> {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!res.ok) {
    const body = await res.text().catch(() => res.statusText);
    onError(body);
    return;
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const raw = line.slice(6).trim();
      if (!raw) continue;
      try {
        const payload = JSON.parse(raw);
        if (payload.error) {
          onError(payload.error as string);
          return;
        }
        if (payload.token) {
          onToken(payload.token as string);
        }
        if (payload.done) {
          onDone((payload.session_id as string) ?? sessionId);
          return;
        }
      } catch {
        // malformed SSE line — skip
      }
    }
  }
}
