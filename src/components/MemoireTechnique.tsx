import { useState } from "react";
import { API_BASE } from "../config";

type MemoTable = {
  enabled: boolean;
  title: string;
  columns: string[];
  rows: string[][];
};

type SubSection = {
  id: string;
  enabled: boolean;
  title: string;
  content: string;
  table: MemoTable;
};

type Chapter = {
  id: string;
  enabled: boolean;
  title: string;
  intro: string;
  sections: SubSection[];
};

const makeId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

const createTable = (): MemoTable => ({
  enabled: false,
  title: "Tableau",
  columns: ["Colonne 1", "Colonne 2"],
  rows: [["", ""]],
});

const createSection = (title = "Sous-chapitre"): SubSection => ({
  id: makeId(),
  enabled: true,
  title,
  content: "",
  table: createTable(),
});

const createChapter = (title = "Nouveau chapitre"): Chapter => ({
  id: makeId(),
  enabled: true,
  title,
  intro: "",
  sections: [createSection("Introduction")],
});

type RagQuestion = { question?: string; reponse?: string };

const parseChapterTitlesFromAnswer = (answer: string): string[] => {
  const normalized = answer.replace(/\r/g, "").trim();
  if (!normalized) return [];
  const lines = normalized.split("\n").map((line) => line.trim()).filter(Boolean);
  const numbered = lines
    .map((line) => line.match(/^\d+\s*[\.\-)]\s*(.+)$/))
    .filter((m): m is RegExpMatchArray => Boolean(m))
    .map((m) => m[1].trim())
    .filter(Boolean);
  if (numbered.length > 0) return numbered;
  return lines.filter((line) => !/^\d+\s*[\.\-)]?$/.test(line));
};

const getInitialChapters = (): Chapter[] => {
  try {
    const raw = sessionStorage.getItem("ragQuestions");
    if (!raw) {
      return [
        createChapter("Notre philosophie et motivation"),
        createChapter("Methodologie et organisation"),
        createChapter("Moyens humains affectes au projet"),
      ];
    }
    const questions = JSON.parse(raw) as RagQuestion[];
    const answer = questions?.[30]?.reponse;
    if (typeof answer !== "string") {
      return [
        createChapter("Notre philosophie et motivation"),
        createChapter("Methodologie et organisation"),
        createChapter("Moyens humains affectes au projet"),
      ];
    }
    const titles = parseChapterTitlesFromAnswer(answer);
    if (titles.length === 0) {
      return [
        createChapter("Notre philosophie et motivation"),
        createChapter("Methodologie et organisation"),
        createChapter("Moyens humains affectes au projet"),
      ];
    }
    return titles.map((title) => createChapter(title));
  } catch {
    return [
      createChapter("Notre philosophie et motivation"),
      createChapter("Methodologie et organisation"),
      createChapter("Moyens humains affectes au projet"),
    ];
  }
};

function MemoireTechnique() {
  const [documentTitle, setDocumentTitle] = useState("MEMOIRE TECHNIQUE");
  const [groupLabel, setGroupLabel] = useState("");
  const [projectTitle, setProjectTitle] = useState("");
  const [intro, setIntro] = useState("");
  const [chapters, setChapters] = useState<Chapter[]>(() => getInitialChapters());
  const [creating, setCreating] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateChapter = (chapterId: string, patch: Partial<Chapter>) => {
    setChapters((prev) => prev.map((c) => (c.id === chapterId ? { ...c, ...patch } : c)));
  };

  const updateSection = (chapterId: string, sectionId: string, patch: Partial<SubSection>) => {
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id !== chapterId
          ? chapter
          : {
              ...chapter,
              sections: chapter.sections.map((s) => (s.id === sectionId ? { ...s, ...patch } : s)),
            }
      )
    );
  };

  const updateTable = (chapterId: string, sectionId: string, patch: Partial<MemoTable>) => {
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id !== chapterId
          ? chapter
          : {
              ...chapter,
              sections: chapter.sections.map((section) =>
                section.id !== sectionId ? section : { ...section, table: { ...section.table, ...patch } }
              ),
            }
      )
    );
  };

  const addChapter = () => {
    setChapters((prev) => [...prev, createChapter()]);
  };

  const removeChapter = (chapterId: string) => {
    setChapters((prev) => prev.filter((chapter) => chapter.id !== chapterId));
  };

  const addSection = (chapterId: string) => {
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id !== chapterId
          ? chapter
          : { ...chapter, sections: [...chapter.sections, createSection()] }
      )
    );
  };

  const removeSection = (chapterId: string, sectionId: string) => {
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id !== chapterId
          ? chapter
          : { ...chapter, sections: chapter.sections.filter((section) => section.id !== sectionId) }
      )
    );
  };

  const addTableColumn = (chapterId: string, sectionId: string) => {
    setChapters((prev) =>
      prev.map((chapter) => {
        if (chapter.id !== chapterId) return chapter;
        return {
          ...chapter,
          sections: chapter.sections.map((section) => {
            if (section.id !== sectionId) return section;
            return {
              ...section,
              table: {
                ...section.table,
                columns: [...section.table.columns, `Colonne ${section.table.columns.length + 1}`],
                rows: section.table.rows.map((row) => [...row, ""]),
              },
            };
          }),
        };
      })
    );
  };

  const removeTableColumn = (chapterId: string, sectionId: string, colIndex: number) => {
    setChapters((prev) =>
      prev.map((chapter) => {
        if (chapter.id !== chapterId) return chapter;
        return {
          ...chapter,
          sections: chapter.sections.map((section) => {
            if (section.id !== sectionId || section.table.columns.length <= 1) return section;
            return {
              ...section,
              table: {
                ...section.table,
                columns: section.table.columns.filter((_, idx) => idx !== colIndex),
                rows: section.table.rows.map((row) => row.filter((_, idx) => idx !== colIndex)),
              },
            };
          }),
        };
      })
    );
  };

  const addTableRow = (chapterId: string, sectionId: string) => {
    setChapters((prev) =>
      prev.map((chapter) => {
        if (chapter.id !== chapterId) return chapter;
        return {
          ...chapter,
          sections: chapter.sections.map((section) =>
            section.id !== sectionId
              ? section
              : {
                  ...section,
                  table: {
                    ...section.table,
                    rows: [...section.table.rows, Array(section.table.columns.length).fill("") as string[]],
                  },
                }
          ),
        };
      })
    );
  };

  const removeTableRow = (chapterId: string, sectionId: string, rowIndex: number) => {
    setChapters((prev) =>
      prev.map((chapter) => {
        if (chapter.id !== chapterId) return chapter;
        return {
          ...chapter,
          sections: chapter.sections.map((section) =>
            section.id !== sectionId || section.table.rows.length <= 1
              ? section
              : {
                  ...section,
                  table: { ...section.table, rows: section.table.rows.filter((_, idx) => idx !== rowIndex) },
                }
          ),
        };
      })
    );
  };

  const updateTableCell = (chapterId: string, sectionId: string, rowIndex: number, colIndex: number, value: string) => {
    setChapters((prev) =>
      prev.map((chapter) => {
        if (chapter.id !== chapterId) return chapter;
        return {
          ...chapter,
          sections: chapter.sections.map((section) => {
            if (section.id !== sectionId) return section;
            return {
              ...section,
              table: {
                ...section.table,
                rows: section.table.rows.map((row, rIdx) =>
                  rIdx !== rowIndex ? row : row.map((cell, cIdx) => (cIdx === colIndex ? value : cell))
                ),
              },
            };
          }),
        };
      })
    );
  };

  const payload = {
    title: documentTitle,
    group_label: groupLabel,
    project_title: projectTitle,
    intro,
    chapters,
  };

  const handleCreate = async () => {
    setCreating(true);
    setDone(false);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/memoire-technique`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(typeof data?.detail === "string" ? data.detail : "Echec de la creation du document");
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur serveur");
    } finally {
      setCreating(false);
    }
  };

  const handleDownload = async () => {
    try {
      const res = await fetch(`${API_BASE}/memoire-technique/download`);
      if (!res.ok) {
        alert("Document non trouve. Creez-le d'abord.");
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "memoire_technique.pdf";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("Impossible de telecharger le document.");
    }
  };

  return (
    <section className="memo-page">
      <div className="memo-header">
        <h1>Memoire technique</h1>
        <p>Composez votre memoire de facon modulable: chapitres, sous-chapitres, textes et tableaux dynamiques.</p>
      </div>

      {error && (
        <div className="memo-error" role="alert">
          {error}
        </div>
      )}

      <div className="memo-card">
        <label>
          Titre principal
          <input value={documentTitle} onChange={(e) => setDocumentTitle(e.target.value)} />
        </label>
        <label>
          Entete equipe / groupement
          <input value={groupLabel} onChange={(e) => setGroupLabel(e.target.value)} placeholder="Ex: ALU - LBEI - CduBeton" />
        </label>
        <label>
          Intitule projet
          <input value={projectTitle} onChange={(e) => setProjectTitle(e.target.value)} />
        </label>
        <label>
          Introduction generale
          <textarea value={intro} onChange={(e) => setIntro(e.target.value)} rows={4} />
        </label>
      </div>

      {chapters.map((chapter, chapterIndex) => (
        <div key={chapter.id} className="memo-card">
          <div className="memo-row">
            <h2>Chapitre {chapterIndex + 1}</h2>
            <button type="button" className="memo-btn-danger" onClick={() => removeChapter(chapter.id)}>
              Supprimer chapitre
            </button>
          </div>
          <label className="memo-inline-check">
            <input type="checkbox" checked={chapter.enabled} onChange={(e) => updateChapter(chapter.id, { enabled: e.target.checked })} />
            Activer ce chapitre
          </label>
          <label>
            Titre du chapitre
            <input value={chapter.title} onChange={(e) => updateChapter(chapter.id, { title: e.target.value })} />
          </label>
          <label>
            Texte introductif du chapitre
            <textarea value={chapter.intro} onChange={(e) => updateChapter(chapter.id, { intro: e.target.value })} rows={4} />
          </label>

          {chapter.sections.map((section, sectionIndex) => (
            <div key={section.id} className="memo-subcard">
              <div className="memo-row">
                <h3>Sous-chapitre {chapterIndex + 1}.{sectionIndex + 1}</h3>
                <button type="button" className="memo-btn-danger" onClick={() => removeSection(chapter.id, section.id)}>
                  Supprimer
                </button>
              </div>
              <label className="memo-inline-check">
                <input
                  type="checkbox"
                  checked={section.enabled}
                  onChange={(e) => updateSection(chapter.id, section.id, { enabled: e.target.checked })}
                />
                Activer ce sous-chapitre
              </label>
              <label>
                Titre
                <input value={section.title} onChange={(e) => updateSection(chapter.id, section.id, { title: e.target.value })} />
              </label>
              <label>
                Contenu
                <textarea value={section.content} onChange={(e) => updateSection(chapter.id, section.id, { content: e.target.value })} rows={5} />
              </label>

              <label className="memo-inline-check">
                <input
                  type="checkbox"
                  checked={section.table.enabled}
                  onChange={(e) => updateTable(chapter.id, section.id, { enabled: e.target.checked })}
                />
                Ajouter un tableau pour ce sous-chapitre
              </label>

              {section.table.enabled && (
                <div className="memo-table-box">
                  <label>
                    Titre du tableau (optionnel)
                    <input value={section.table.title} onChange={(e) => updateTable(chapter.id, section.id, { title: e.target.value })} />
                  </label>
                  <div className="memo-table-actions">
                    <button type="button" onClick={() => addTableColumn(chapter.id, section.id)}>
                      + Colonne
                    </button>
                    <button type="button" onClick={() => addTableRow(chapter.id, section.id)}>
                      + Ligne
                    </button>
                  </div>
                  <div className="memo-table-scroll">
                    <table className="memo-table">
                      <thead>
                        <tr>
                          {section.table.columns.map((col, colIndex) => (
                            <th key={`col-${section.id}-${colIndex}`}>
                              <input
                                value={col}
                                onChange={(e) => {
                                  const next = [...section.table.columns];
                                  next[colIndex] = e.target.value;
                                  updateTable(chapter.id, section.id, { columns: next });
                                }}
                              />
                              <button type="button" className="memo-icon-btn" onClick={() => removeTableColumn(chapter.id, section.id, colIndex)}>
                                ×
                              </button>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {section.table.rows.map((row, rowIndex) => (
                          <tr key={`row-${section.id}-${rowIndex}`}>
                            {row.map((cell, colIndex) => (
                              <td key={`cell-${section.id}-${rowIndex}-${colIndex}`}>
                                <input
                                  value={cell}
                                  onChange={(e) => updateTableCell(chapter.id, section.id, rowIndex, colIndex, e.target.value)}
                                />
                              </td>
                            ))}
                            <td className="memo-row-delete">
                              <button type="button" className="memo-icon-btn" onClick={() => removeTableRow(chapter.id, section.id, rowIndex)}>
                                ×
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          ))}

          <button type="button" className="memo-btn-soft" onClick={() => addSection(chapter.id)}>
            + Ajouter un sous-chapitre
          </button>
        </div>
      ))}

      <div className="memo-actions">
        <button type="button" className="memo-btn-soft" onClick={addChapter}>
          + Ajouter un chapitre
        </button>
        <button type="button" className="memo-btn-primary" onClick={handleCreate} disabled={creating}>
          {creating ? "Creation..." : done ? "✓ Document cree" : "Creer le document"}
        </button>
        <button type="button" className="memo-btn-secondary" onClick={handleDownload}>
          Telecharger
        </button>
      </div>
    </section>
  );
}

export default MemoireTechnique;
