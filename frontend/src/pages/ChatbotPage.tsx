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
          <h2 style={{ fontSize: '0.9rem', fontWeight: 600, margin: '0 0 0.75rem' }}>
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
            <p style={{ color: '#e53e3e', fontSize: '0.75rem', margin: '0 0 0.5rem' }}>
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
