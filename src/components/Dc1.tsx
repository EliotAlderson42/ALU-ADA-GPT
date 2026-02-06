import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

type DataItem = { keyword: string; answer: string };

function Dc1() {
  const [items, setItems] = useState<DataItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const raw = sessionStorage.getItem("ragData");
    if (!raw) {
      setItems([]);
      setLoading(false);
      return;
    }
    try {
      const parsed = JSON.parse(raw) as unknown;
      const list = Array.isArray(parsed) ? parsed : [];
      const normalized: DataItem[] = list
        .filter((el): el is [string, string] | { keyword?: string; answer?: string } => el != null)
        .map((el) => {
          if (Array.isArray(el)) {
            return { keyword: String(el[0] ?? ""), answer: String(el[1] ?? "") };
          }
          return { keyword: String(el.keyword ?? ""), answer: String(el.answer ?? "") };
        })
        .filter((e) => e.keyword || e.answer);
      const last5 = normalized.slice(-5);
      setItems(last5);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleChange = (index: number, field: "keyword" | "answer", value: string) => {
    setItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, [field]: value } : item))
    );
    setSaved(false);
  };

  const handleSave = () => {
    const raw = sessionStorage.getItem("ragData");
    if (!raw) return;
    try {
      const parsed = JSON.parse(raw) as unknown[];
      const list = Array.isArray(parsed) ? parsed : [];
      const head = list.slice(0, -items.length);
      const tail = items.map((i) => [i.keyword, i.answer] as [string, string]);
      sessionStorage.setItem("ragData", JSON.stringify([...head, ...tail]));
      setSaved(true);
    } catch {
      sessionStorage.setItem(
        "ragData",
        JSON.stringify(items.map((i) => [i.keyword, i.answer]))
      );
      setSaved(true);
    }
  };

  if (loading) return <p className="dc1-loading">Chargement…</p>;
  if (items.length === 0)
    return (
      <section className="dc1-page">
        <h1>DC1</h1>
        <p>Aucune donnée disponible. Analysez d'abord un PDF depuis l'accueil.</p>
        <Link to="/" className="dc1-back">
          ← Retour à l'accueil
        </Link>
      </section>
    );

  return (
    <section className="dc1-page">
      <h1>DC1 — Derniers 5 éléments</h1>
      <p className="dc1-intro">
        Modifiez les 5 derniers éléments de data puis enregistrez.
      </p>

      <ul className="dc1-list">
        {items.map((item, index) => (
          <li key={index} className="dc1-card">
            <label>
              <span className="dc1-label">Mot-clé</span>
              <input
                type="text"
                value={item.keyword}
                onChange={(e) => handleChange(index, "keyword", e.target.value)}
              />
            </label>
            <label>
              <span className="dc1-label">Réponse</span>
              <textarea
                value={item.answer}
                onChange={(e) => handleChange(index, "answer", e.target.value)}
                rows={3}
              />
            </label>
          </li>
        ))}
      </ul>

      <div className="dc1-actions">
        <button type="button" className="dc1-save" onClick={handleSave}>
          {saved ? "✓ Enregistré" : "Enregistrer les modifications"}
        </button>
        <Link to="/results" className="dc1-back">
          ← Retour aux résultats
        </Link>
      </div>
    </section>
  );
}

export default Dc1;
