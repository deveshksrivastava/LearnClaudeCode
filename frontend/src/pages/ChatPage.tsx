import { useEffect, useRef, useState } from 'react';
import { streamChat, newChatSession, clearChatHistory } from '../api/chat';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const SESSION_KEY = 'shopfast_chat_session';

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  // Initialise or restore session
  useEffect(() => {
    const saved = sessionStorage.getItem(SESSION_KEY);
    if (saved) {
      setSessionId(saved);
    } else {
      newChatSession().then((id) => {
        sessionStorage.setItem(SESSION_KEY, id);
        setSessionId(id);
      });
    }
  }, []);

  // Auto-scroll on new content
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text || streaming || !sessionId) return;

    setInput('');
    setError('');
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setStreaming(true);

    // Add placeholder for streaming assistant reply
    setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);

    await streamChat(
      text,
      sessionId,
      (token) => {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: 'assistant',
            content: updated[updated.length - 1].content + token,
          };
          return updated;
        });
      },
      (finalSession) => {
        sessionStorage.setItem(SESSION_KEY, finalSession);
        setSessionId(finalSession);
        setStreaming(false);
      },
      (err) => {
        setError(err);
        // Remove empty placeholder on error
        setMessages((prev) => {
          const updated = [...prev];
          if (updated[updated.length - 1].content === '') updated.pop();
          return updated;
        });
        setStreaming(false);
      },
    );
  }

  async function handleClear() {
    if (!sessionId) return;
    await clearChatHistory(sessionId);
    sessionStorage.removeItem(SESSION_KEY);
    const id = await newChatSession();
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
        <h1 className="page-title" style={{ marginBottom: 0 }}>ShopFast Assistant</h1>
        <button className="chat-clear-btn" onClick={handleClear} disabled={streaming}>
          New conversation
        </button>
      </div>

      <div className="chat-window">
        {messages.length === 0 && (
          <div className="chat-empty">
            Ask me anything about our products — pricing, stock, recommendations!
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble chat-bubble--${msg.role}`}>
            <span className="chat-role">{msg.role === 'user' ? 'You' : 'Assistant'}</span>
            <p className="chat-content">{msg.content}{streaming && i === messages.length - 1 && msg.role === 'assistant' && <span className="chat-cursor" />}</p>
          </div>
        ))}

        {error && <p className="status-msg error">Error: {error}</p>}
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
          disabled={streaming}
        />
        <button
          className="chat-send-btn"
          onClick={send}
          disabled={streaming || !input.trim()}
        >
          {streaming ? '…' : 'Send'}
        </button>
      </div>
    </div>
  );
}
