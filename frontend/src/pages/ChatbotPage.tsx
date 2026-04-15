import { useEffect, useRef, useState } from 'react';
import { sendMessage, newSessionId, uploadDocument, type ChatMessage } from '../api/chatbotApi';

const SESSION_KEY = 'chatbot_session_id';

export default function ChatbotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  // Upload state
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{ ok: boolean; msg: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Restore or create a session ID on mount
  useEffect(() => {
    const saved = sessionStorage.getItem(SESSION_KEY);
    const id = saved ?? newSessionId();
    if (!saved) sessionStorage.setItem(SESSION_KEY, id);
    setSessionId(id);
  }, []);

  // Auto-scroll whenever messages or loading state changes
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
      const data = await sendMessage(text, sessionId);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response, sources: data.sources },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  }

  function startNewConversation() {
    const id = newSessionId();
    sessionStorage.setItem(SESSION_KEY, id);
    setSessionId(id);
    setMessages([]);
    setError('');
  }

  async function handleUpload() {
    if (!uploadFile || uploading) return;
    setUploading(true);
    setUploadStatus(null);
    try {
      const data = await uploadDocument(uploadFile);
      setUploadStatus({ ok: true, msg: `"${data.filename}" indexed as ${data.indexed_chunks} chunk(s).` });
      setUploadFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      setUploadStatus({ ok: false, msg: err instanceof Error ? err.message : 'Upload failed.' });
    } finally {
      setUploading(false);
    }
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
        <button className="chat-clear-btn" onClick={startNewConversation} disabled={loading}>
          New conversation LMCHATING
        </button>
      </div>

      {/* Upload strip */}
      <div className="flex items-center gap-3 flex-shrink-0 flex-wrap">
        <label className="flex items-center gap-2 px-3 py-1.5 border border-dashed border-gray-300 rounded-lg text-sm text-gray-500 bg-gray-50 cursor-pointer hover:border-indigo-400 hover:text-indigo-500 transition-colors max-w-xs truncate">
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.pdf,.md"
            className="sr-only"
            onChange={(e) => {
              setUploadFile(e.target.files?.[0] ?? null);
              setUploadStatus(null);
            }}
            disabled={uploading}
          />
          {uploadFile ? uploadFile.name : 'Choose .txt / .pdf / .md…'}
        </label>
        <button
          className="px-4 py-1.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          onClick={handleUpload}
          disabled={!uploadFile || uploading}
        >
          {uploading ? 'Uploading…' : 'Upload'}
        </button>
        {uploadStatus && (
          <span className={`text-xs px-3 py-1 rounded-full font-medium ${uploadStatus.ok ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {uploadStatus.msg}
          </span>
        )}
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
