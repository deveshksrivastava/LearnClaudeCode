import { useEffect, useRef, useState } from 'react';
import { uploadFiles, getDocuments, deleteDocument } from '../api/chatbotApi';

const LLM_CHAT_URL = 'http://127.0.0.1:8002/api/v1/chat-llm';
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

  // Document panel state
  const [documents, setDocuments] = useState<string[]>([]);
  const [docsLoading, setDocsLoading] = useState(false);
  const [docsError, setDocsError] = useState('');
  const [uploadStatus, setUploadStatus] = useState('');
  const [deletingFile, setDeletingFile] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const saved = sessionStorage.getItem(SESSION_KEY);
    const id = saved ?? generateSessionId();
    if (!saved) sessionStorage.setItem(SESSION_KEY, id);
    setSessionId(id);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Load documents on mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  async function fetchDocuments() {
    setDocsLoading(true);
    setDocsError('');
    try {
      const result = await getDocuments();
      setDocuments(result.documents);
    } catch (err) {
      setDocsError(err instanceof Error ? err.message : 'Failed to load documents.');
    } finally {
      setDocsLoading(false);
    }
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploadStatus('Uploading…');
    setDocsError('');
    try {
      const result = await uploadFiles(files);
      setUploadStatus(result.message);
      await fetchDocuments();
    } catch (err) {
      setDocsError(err instanceof Error ? err.message : 'Upload failed.');
      setUploadStatus('');
    } finally {
      // Reset the file input so the same file can be re-uploaded if needed
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  }

  async function handleDeleteDocument(filename: string) {
    setDeletingFile(filename);
    setDocsError('');
    try {
      await deleteDocument(filename);
      await fetchDocuments();
    } catch (err) {
      setDocsError(err instanceof Error ? err.message : 'Delete failed.');
    } finally {
      setDeletingFile(null);
    }
  }

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
    <div className="llm-chat-with-sidebar">
      {/* ── Left: Chat area ── */}
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

      {/* ── Right: Document management panel ── */}
      <aside className="docs-panel">
        <div className="docs-panel-header">
          <h2 className="docs-panel-title">Knowledge Base</h2>
          <button
            className="docs-upload-btn"
            onClick={() => fileInputRef.current?.click()}
            disabled={docsLoading}
          >
            + Upload
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".txt,.pdf,.md"
            style={{ display: 'none' }}
            onChange={handleFileUpload}
          />
        </div>

        {uploadStatus && (
          <p className="docs-status docs-status--success">{uploadStatus}</p>
        )}
        {docsError && (
          <p className="docs-status docs-status--error">{docsError}</p>
        )}

        <div className="docs-list">
          {docsLoading && <p className="docs-empty">Loading…</p>}

          {!docsLoading && documents.length === 0 && (
            <p className="docs-empty">No documents uploaded yet.</p>
          )}

          {!docsLoading && documents.map((doc) => (
            <div key={doc} className="docs-item">
              <span className="docs-item-name" title={doc}>{doc}</span>
              <button
                className="docs-delete-btn"
                onClick={() => handleDeleteDocument(doc)}
                disabled={deletingFile === doc}
                title={`Delete ${doc}`}
              >
                {deletingFile === doc ? '…' : '✕'}
              </button>
            </div>
          ))}
        </div>
      </aside>
    </div>
  );
}
