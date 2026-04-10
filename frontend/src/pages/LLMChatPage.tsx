import { useEffect, useRef, useState } from 'react';

const LLM_CHAT_URL = 'http://127.0.0.1:800ssds2/api/v1/chat-llm';
const SESSION_KEY = 'llm_chat_session_id';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

interface ChatResponse {
  session_id: string;
  response: string;
  sources?: string[];
}

function generateSessionId(): string {
  return `user-${crypto.randomUUID()}`;
}

export default function LLMChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const saved = sessionStorage.getItem(SESSION_KEY);
    const id = saved ?? generateSessionId();
    if (!saved) sessionStorage.setItem(SESSION_KEY, id);
    setSessionId(id);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  async function send() {
    const text = input.trim();
    if (!text || loading || !sessionId) return;

    setInput('');
    setError('');
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setLoading(true);

    try {
      const res = await fetch(LLM_CHAT_URL, {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId, message: text }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error((body as { detail?: string }).detail ?? 'Chat request failed');
      }

      const data: ChatResponse = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          sources: data.sources,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  }

  function startNewConversation() {
    const id = generateSessionId();
    sessionStorage.setItem(SESSION_KEY, id);
    setSessionId(id);
    setMessages([]);
    setError('');
  }

  function handleKey(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="page chat-page">
      <div className="chat-header">
        <h1 className="page-title" style={{ marginBottom: 0 }}>AI Support Chat</h1>
        <button className="chat-clear-btn" onClick={startNewConversation} disabled={loading}>
          New conversation AI LLM
        </button>
      </div>

      <div className="chat-window">
        {messages.length === 0 && !loading && (
          <div className="chat-empty">
            Ask me anything — return policies, product info, order help, and more!
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble chat-bubble--${msg.role}`}>
            <span className="chat-role">{msg.role === 'user' ? 'You' : 'AI Support'}</span>
            <p className="chat-content">{msg.content}</p>
            {msg.sources && msg.sources.length > 0 && (
              <p className="chat-sources">Sources: {msg.sources.join(', ')}</p>
            )}
          </div>
        ))}

        {loading && (
          <div className="chat-bubble chat-bubble--assistant">
            <span className="chat-role">AI Support</span>
            <p className="chat-content chat-thinking">
              <span className="chat-dot" />
              <span className="chat-dot" />
              <span className="chat-dot" />
            </p>
          </div>
        )}

        {error && <p className="status-msg error">Error: {error}</p>}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-row">
        <textarea
          className="chat-textarea"
          rows={2}
          placeholder="Ask about return policies, products, orders…"
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
  );
}
