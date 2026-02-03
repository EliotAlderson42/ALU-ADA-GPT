import { useState, useEffect } from "react";

const API_BASE = "http://127.0.0.1:8011";

export type QuestionRag = {
  id: number;
  llm: string;
  rerank: string;
  user: string;
  keyword: string;
  order_index?: number;
};

function Questions() {
  const [questions, setQuestions] = useState<QuestionRag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ llm: "", rerank: "", user: "", keyword: "" });
  const [submitting, setSubmitting] = useState(false);

  const fetchQuestions = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/questions`);
      if (!res.ok) throw new Error("Impossible de charger les questions");
      const data = await res.json();
      setQuestions(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur réseau");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.llm.trim() || !form.rerank.trim() || !form.user.trim() || !form.keyword.trim()) {
      setError("Tous les champs sont requis.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/questions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Erreur lors de l'ajout");
      }
      const created = await res.json();
      setQuestions((prev) => [...prev, created]);
      setForm({ llm: "", rerank: "", user: "", keyword: "" });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Supprimer cette question ?")) return;
    try {
      const res = await fetch(`${API_BASE}/questions/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Suppression impossible");
      setQuestions((prev) => prev.filter((q) => q.id !== id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur");
    }
  };

  return (
    <section className="questions-page">
      <h1>Questions RAG</h1>
      <p className="questions-intro">
        Ces questions sont posées au document lors de l'analyse PDF. Tu peux en ajouter ou en supprimer.
      </p>

      {error && (
        <div className="error-message">
          <strong>Erreur :</strong> {error}
        </div>
      )}

      <form className="questions-form" onSubmit={handleSubmit}>
        <h2>Ajouter une question</h2>
        <label>
          Question (utilisateur) *
          <input
            value={form.user}
            onChange={(e) => setForm((f) => ({ ...f, user: e.target.value }))}
            placeholder="Ex: Quel est le montant des travaux ?"
            required
          />
        </label>
        <label>
          Question (LLM / détail) *
          <input
            value={form.llm}
            onChange={(e) => setForm((f) => ({ ...f, llm: e.target.value }))}
            placeholder="Question détaillée pour le modèle"
            required
          />
        </label>
        <label>
          Rerank (recherche sémantique) *
          <input
            value={form.rerank}
            onChange={(e) => setForm((f) => ({ ...f, rerank: e.target.value }))}
            placeholder="Ex: Montant/prix prévisionnel du projet"
            required
          />
        </label>
        <label>
          Mot-clé (identifiant) *
          <input
            value={form.keyword}
            onChange={(e) => setForm((f) => ({ ...f, keyword: e.target.value }))}
            placeholder="Ex: Travaux"
            required
          />
        </label>
        <button type="submit" disabled={submitting}>
          {submitting ? "Ajout..." : "Ajouter la question"}
        </button>
      </form>

      <div className="questions-list-wrap">
        <h2>Liste des questions ({questions.length})</h2>
        {loading ? (
          <p>Chargement...</p>
        ) : questions.length === 0 ? (
          <p>Aucune question. Ajoute-en une ci-dessus.</p>
        ) : (
          <ul className="questions-list">
            {questions.map((q) => (
              <li key={q.id} className="question-rag-card">
                <div className="question-rag-header">
                  <span className="question-rag-keyword">{q.keyword}</span>
                  <button
                    type="button"
                    className="question-rag-delete"
                    onClick={() => handleDelete(q.id)}
                    title="Supprimer"
                  >
                    ×
                  </button>
                </div>
                <p className="question-rag-user">{q.user}</p>
                <p className="question-rag-llm">{q.llm}</p>
                <p className="question-rag-rerank">Rerank : {q.rerank}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}

export default Questions;
