import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import type { Question } from "../App";
import { normalizeNewlines } from "../utils";

const API_BASE = "http://127.0.0.1:8011";

type ResultsProps = {
  questions: Question[];
};

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  question?: string;
  keyword?: string;
  rerank?: string;
  content: string;
};

function Results({ questions }: ResultsProps) {
  const [chatOpen, setChatOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [keyword, setKeyword] = useState("");
  const [rerankQuestion, setRerankQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = question.trim();
    if (!q) return;
    setLoading(true);
    setError(null);
    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      question: q,
      keyword: keyword.trim() || undefined,
      rerank: rerankQuestion.trim() || undefined,
      content: q,
    };
    setMessages((prev) => [...prev, userMsg]);
    setQuestion("");
    setKeyword("");
    setRerankQuestion("");
    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: q,
          keyword: keyword.trim() || undefined,
          rerank: rerankQuestion.trim() || q,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Erreur lors de l'envoi");
      }
      const assistantMsg: ChatMessage = {
        id: `a-${Date.now()}`,
        role: "assistant",
        content: data.reponse ?? "",
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="results">
      <h1>Résultats</h1>

      <Link to="/dc1" className="results-dc1-btn">
        Start DC1
      </Link>

      {questions.length === 0 ? (
        <p>Aucune question à afficher pour le moment.</p>
      ) : (
        <ul className="results-list">
          {questions.map((q, index) => (
            <li key={index} className="question-card">
              <h2>Question {index + 1}</h2>
              <p className="question-text">{q.question}</p>
              <p className="answer-text">{normalizeNewlines(q.reponse)}</p>
            </li>
          ))}
        </ul>
      )}

      {/* Bouton flottant fixe (visible partout sur la page) */}
      <button
        type="button"
        className="results-chat-fab"
        onClick={() => setChatOpen(true)}
        aria-label="Ouvrir le chat PDF"
        title="Chat PDF — question supplémentaire"
      >
        <span className="results-chat-fab-icon" aria-hidden>💬</span>
        <span className="results-chat-fab-label">Chat PDF</span>
      </button>

      {chatOpen && (
        <div className="results-chat-overlay results-chat-overlay--side" aria-modal="true" role="dialog" aria-labelledby="chat-title">
          <div className="results-chat-backdrop" onClick={() => setChatOpen(false)} />
          <div className="results-chat-window results-chat-window--side">
            <div className="results-chat-header">
              <h2 id="chat-title" className="results-chat-title">Chat PDF</h2>
              <button
                type="button"
                className="results-chat-close"
                onClick={() => setChatOpen(false)}
                aria-label="Fermer"
              >
                ×
              </button>
            </div>
            <p className="results-chat-desc">
              Question LLM + <strong>keyword</strong> + <strong>rerank</strong> → <code>add_question</code>.
            </p>
            <div className="results-chat-messages" role="log" aria-live="polite">
              {messages.length === 0 && (
                <p className="results-chat-empty">Aucun message. Pose une question ci-dessous.</p>
              )}
              {messages.map((m) => (
                <div key={m.id} className={`results-chat-bubble results-chat-bubble--${m.role}`}>
                  {m.role === "user" && (m.keyword || m.rerank) && (
                    <div className="results-chat-meta">
                      {m.keyword && <span className="results-chat-tag">keyword: {m.keyword}</span>}
                      {m.rerank && <span className="results-chat-tag">rerank: {m.rerank}</span>}
                    </div>
                  )}
                  <p className="results-chat-content">{m.content ? normalizeNewlines(m.content) : "…"}</p>
                </div>
              ))}
              {loading && (
                <div className="results-chat-bubble results-chat-bubble--assistant">
                  <p className="results-chat-content results-chat-loading">Réponse en cours…</p>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
            <form onSubmit={handleSend} className="results-chat-form">
              <div className="results-chat-fields">
                <label>
                  Question LLM *
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Question pour le modèle"
                    disabled={loading}
                  />
                </label>
                <label>
                  Keyword
                  <input
                    type="text"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    placeholder="Ex: Travaux, Type"
                    disabled={loading}
                  />
                </label>
                <label>
                  Rerank
                  <input
                    type="text"
                    value={rerankQuestion}
                    onChange={(e) => setRerankQuestion(e.target.value)}
                    placeholder="Ex: Montant prévisionnel"
                    disabled={loading}
                  />
                </label>
              </div>
              <div className="results-chat-actions">
                <button type="submit" disabled={loading || !question.trim()}>
                  {loading ? "Envoi…" : "Envoyer"}
                </button>
              </div>
            </form>
            {error && (
              <p className="results-chat-error" role="alert">
                {error}
              </p>
            )}
          </div>
        </div>
      )}
    </section>
  );
}

export default Results;
