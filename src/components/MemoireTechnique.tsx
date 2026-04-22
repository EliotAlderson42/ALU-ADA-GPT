import { useEffect, useState } from "react";
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
  selectedPhases: string[];
  administrations: {
    id: number;
    name: string;
    description: string;
    rolePhaseEtudes: string;
    rolePhaseChantier: string;
    moyensHumains: { id: string; nom: string; description: string }[];
  }[];
  adminMode: "existing" | "new";
  existingAdministrationId: number | null;
  newAdministrationName: string;
  implicationMatrix: {
    label: string;
    valuesByAdmin: Record<string, string[]>;
  }[];
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
  selectedPhases: [],
  administrations: [],
  adminMode: "existing",
  existingAdministrationId: null,
  newAdministrationName: "",
  implicationMatrix: [],
  table: createTable(),
});

const PHASE_OPTIONS = ["ESQ", "AVP", "Autorisation Admin.", "PRO", "DCE", "ACT", "VISA", "DET", "AOR", "OPC"];

const isLivrablesSection = (title: string): boolean => {
  const normalized = title
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();
  return normalized.includes("livrables et delais de realisation des prestations par phase");
};

const isMoyensHumainsSection = (title: string): boolean => {
  const normalized = title
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();
  return normalized.includes("moyens humains affect");
};

const isRoleIntervenantsSection = (title: string): boolean => {
  const normalized = title
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();
  return normalized.includes("role des intervenants de la moe");
};

const isImplicationsSection = (title: string): boolean => {
  const normalized = title
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();
  return normalized.includes("implications des membres de l'equipe durant la mission");
};

const IMPLICATION_ROWS = [
  "ESQUISSE",
  "AVP",
  "PC",
  "ETUDES THERMIQUES",
  "PRO",
  "REUNIONS CONCEPTION",
  "REUNIONS COORDINATION",
  "DCE",
  "ANALYSE DES OFFRES TVX",
  "VISA CE TECHNIQUES",
  "VISA CE ARCHITECTURAUX",
  "DET SUIVI DE CHANTIER",
  "DET SUIVI FINANCIER",
  "AOR OPR DOE",
  "AOR GPA",
  "OPC",
];

const buildImplicationMatrix = (
  adminIds: number[],
  previous: { label: string; valuesByAdmin: Record<string, string[]> }[] = []
) =>
  IMPLICATION_ROWS.map((label) => {
    const prevRow = previous.find((r) => r.label === label);
    const valuesByAdmin: Record<string, string[]> = {};
    adminIds.forEach((id) => {
      const key = String(id);
      valuesByAdmin[key] = Array.isArray(prevRow?.valuesByAdmin?.[key]) ? prevRow!.valuesByAdmin[key] : [];
    });
    return { label, valuesByAdmin };
  });

const getDefaultSectionTitlesForChapter = (chapterTitle: string): string[] => {
  const normalized = chapterTitle
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();

  if (normalized === "methodologie et organisation") {
    return [
      "1. Livrables et delais de realisation des prestations par phase",
      "2. Moyens humains affectes au projet",
      "3. Role des intervenants de la MOE",
      "4. Implications des membres de l'equipe durant la mission",
      "5. Demarche qualite",
    ];
  }

  return ["Introduction"];
};

const buildSectionsForChapter = (chapterTitle: string): SubSection[] =>
  getDefaultSectionTitlesForChapter(chapterTitle).map((title) => createSection(title));

const createChapter = (title = "Nouveau chapitre"): Chapter => ({
  id: makeId(),
  enabled: true,
  title,
  intro: "",
  sections: buildSectionsForChapter(title),
});

type RagQuestion = { question?: string; reponse?: string };

const normalizeTextForCompare = (value: string): string =>
  value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();

const CHAPTER_SOURCE_QUESTION = "Quels sont les points a prendre en compte pour la création de la note methodologique ?";

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
  const fallbackChapters = [
    createChapter("Notre philosophie et motivation"),
    createChapter("Methodologie et organisation"),
    createChapter("Moyens humains affectes au projet"),
  ];

  try {
    const raw = sessionStorage.getItem("ragQuestions");
    if (!raw) {
      return fallbackChapters;
    }
    const questions = JSON.parse(raw) as RagQuestion[];
    const targetQuestion = questions.find(
      (item) =>
        typeof item?.question === "string" &&
        normalizeTextForCompare(item.question) === normalizeTextForCompare(CHAPTER_SOURCE_QUESTION)
    );
    const answer =
      typeof targetQuestion?.reponse === "string"
        ? targetQuestion.reponse
        : typeof questions?.[30]?.reponse === "string"
          ? questions[30].reponse
          : null;

    if (typeof answer !== "string") {
      return fallbackChapters;
    }
    const titles = parseChapterTitlesFromAnswer(answer);
    if (titles.length === 0) {
      return fallbackChapters;
    }
    return titles.map((title) => createChapter(title));
  } catch {
    return fallbackChapters;
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
  const [availableAdministrations, setAvailableAdministrations] = useState<{ id: number; name: string }[]>([]);
  const [loadedProfileIds, setLoadedProfileIds] = useState<number[]>([]);

  useEffect(() => {
    const fetchAdministrations = async () => {
      try {
        const res = await fetch(`${API_BASE}/memoire-technique/administrations`);
        if (!res.ok) return;
        const data = await res.json();
        if (Array.isArray(data)) {
          setAvailableAdministrations(
            data
              .filter((a): a is { id: number; name: string } => typeof a?.id === "number" && typeof a?.name === "string")
              .map((a) => ({ id: a.id, name: a.name }))
          );
        }
      } catch {
        // ignore
      }
    };
    fetchAdministrations();
  }, []);

  const updateChapter = (chapterId: string, patch: Partial<Chapter>) => {
    setChapters((prev) =>
      prev.map((chapter) => {
        if (chapter.id !== chapterId) return chapter;
        if (typeof patch.title !== "string") return { ...chapter, ...patch };
        return {
          ...chapter,
          ...patch,
          sections: buildSectionsForChapter(patch.title),
        };
      })
    );
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

  const toggleImplicationValue = (
    chapterId: string,
    sectionId: string,
    rowLabel: string,
    adminId: number,
    value: "P" | "C" | "E"
  ) => {
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id !== chapterId
          ? chapter
          : {
              ...chapter,
              sections: chapter.sections.map((section) => {
                if (section.id !== sectionId) return section;
                return {
                  ...section,
                  implicationMatrix: section.implicationMatrix.map((row) => {
                    if (row.label !== rowLabel) return row;
                    const key = String(adminId);
                    const current = row.valuesByAdmin[key] ?? [];
                    const next = current.includes(value)
                      ? current.filter((v) => v !== value)
                      : [...current, value];
                    return {
                      ...row,
                      valuesByAdmin: { ...row.valuesByAdmin, [key]: next },
                    };
                  }),
                };
              }),
            }
      )
    );
  };

  const fetchAdministrationProfile = async (administrationId: number) => {
    const res = await fetch(`${API_BASE}/memoire-technique/administrations/${administrationId}/profile`);
    if (!res.ok) return null;
    const p = await res.json();
    return {
      id: Number(p?.id),
      name: String(p?.name ?? ""),
      description: String(p?.description ?? ""),
      rolePhaseEtudes: String(p?.rolePhaseEtudes ?? ""),
      rolePhaseChantier: String(p?.rolePhaseChantier ?? ""),
      moyensHumains:
        Array.isArray(p?.moyensHumains) && p.moyensHumains.length > 0
          ? p.moyensHumains.map((mh: { nom?: string; description?: string }) => ({
              id: makeId(),
              nom: String(mh?.nom ?? ""),
              description: String(mh?.description ?? ""),
            }))
          : [{ id: makeId(), nom: "", description: "" }],
    };
  };

  const addExistingAdministrationToSection = async (chapterId: string, sectionId: string) => {
    const targetSection = chapters.flatMap((c) => c.sections).find((s) => s.id === sectionId);
    const administrationId = targetSection?.existingAdministrationId;
    if (!administrationId) return;

    const fallback = availableAdministrations.find((a) => a.id === administrationId);
    const profile = await fetchAdministrationProfile(administrationId);
    const adminToInsert = profile ?? {
      id: administrationId,
      name: fallback?.name ?? "",
      description: "",
      rolePhaseEtudes: "",
      rolePhaseChantier: "",
      moyensHumains: [{ id: makeId(), nom: "", description: "" }],
    };

    setChapters((prev) =>
      prev.map((chapter) => {
        if (chapter.id !== chapterId) return chapter;
        return {
          ...chapter,
          sections: chapter.sections.map((section) => {
            if (section.id !== sectionId) return section;
            if (section.administrations.some((a) => a.id === adminToInsert.id)) return section;
            return {
              ...section,
              administrations: [...section.administrations, adminToInsert],
            };
          }),
        };
      })
    );
    setLoadedProfileIds((prev) => (prev.includes(administrationId) ? prev : [...prev, administrationId]));
  };

  const addNewAdministrationToSection = async (chapterId: string, sectionId: string) => {
    const targetSection = chapters
      .flatMap((c) => c.sections)
      .find((s) => s.id === sectionId);
    const name = (targetSection?.newAdministrationName ?? "").trim();
    if (!name) {
      setError("Nom d'administration requis.");
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/memoire-technique/administrations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(typeof data?.detail === "string" ? data.detail : "Creation administration impossible");
      const created = { id: Number(data.id), name: String(data.name ?? "") };
      if (!Number.isFinite(created.id) || !created.name) throw new Error("Réponse API invalide");
      setAvailableAdministrations((prev) =>
        prev.some((a) => a.id === created.id) ? prev : [...prev, created]
      );
      setChapters((prev) =>
        prev.map((chapter) => {
          if (chapter.id !== chapterId) return chapter;
          return {
            ...chapter,
            sections: chapter.sections.map((section) => {
              if (section.id !== sectionId) return section;
              if (section.administrations.some((a) => a.id === created.id)) {
                return { ...section, newAdministrationName: "" };
              }
              return {
                ...section,
                newAdministrationName: "",
                administrations: [
                  ...section.administrations,
                  {
                    id: created.id,
                    name: created.name,
                    description: String(data?.description ?? ""),
                    rolePhaseEtudes: String(data?.rolePhaseEtudes ?? ""),
                    rolePhaseChantier: String(data?.rolePhaseChantier ?? ""),
                    moyensHumains: [{ id: makeId(), nom: "", description: "" }],
                  },
                ],
              };
            }),
          };
        })
      );
      setLoadedProfileIds((prev) => (prev.includes(created.id) ? prev : [...prev, created.id]));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur creation administration");
    }
  };

  const removeAdministrationFromSection = (chapterId: string, sectionId: string, administrationId: number) => {
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id !== chapterId
          ? chapter
          : {
              ...chapter,
              sections: chapter.sections.map((section) =>
                section.id !== sectionId
                  ? section
                  : { ...section, administrations: section.administrations.filter((a) => a.id !== administrationId) }
              ),
            }
      )
    );
  };

  const deleteAdministrationFromDatabase = async (administrationId: number) => {
    if (!confirm("Supprimer cette administration de la base de données ?")) return;
    try {
      const res = await fetch(`${API_BASE}/memoire-technique/administrations/${administrationId}`, {
        method: "DELETE",
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(typeof data?.detail === "string" ? data.detail : "Suppression impossible");
      }
      setAvailableAdministrations((prev) => prev.filter((a) => a.id !== administrationId));
      setLoadedProfileIds((prev) => prev.filter((id) => id !== administrationId));
      setChapters((prev) =>
        prev.map((chapter) => ({
          ...chapter,
          sections: chapter.sections.map((section) => ({
            ...section,
            administrations: section.administrations.filter((a) => a.id !== administrationId),
            existingAdministrationId:
              section.existingAdministrationId === administrationId ? null : section.existingAdministrationId,
          })),
        }))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de la suppression");
    }
  };

  const addMoyenHumain = (chapterId: string, sectionId: string, administrationId: number) => {
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id !== chapterId
          ? chapter
          : {
              ...chapter,
              sections: chapter.sections.map((section) =>
                section.id !== sectionId
                  ? section
                  : {
                      ...section,
                      administrations: section.administrations.map((a) =>
                        a.id !== administrationId
                          ? a
                          : { ...a, moyensHumains: [...a.moyensHumains, { id: makeId(), nom: "", description: "" }] }
                      ),
                    }
              ),
            }
      )
    );
  };

  const updateMoyenHumain = (
    chapterId: string,
    sectionId: string,
    administrationId: number,
    moyenId: string,
    patch: { nom?: string; description?: string }
  ) => {
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id !== chapterId
          ? chapter
          : {
              ...chapter,
              sections: chapter.sections.map((section) =>
                section.id !== sectionId
                  ? section
                  : {
                      ...section,
                      administrations: section.administrations.map((a) =>
                        a.id !== administrationId
                          ? a
                          : {
                              ...a,
                              moyensHumains: a.moyensHumains.map((m) => (m.id === moyenId ? { ...m, ...patch } : m)),
                            }
                      ),
                    }
              ),
            }
      )
    );
  };

  const removeMoyenHumain = (chapterId: string, sectionId: string, administrationId: number, moyenId: string) => {
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id !== chapterId
          ? chapter
          : {
              ...chapter,
              sections: chapter.sections.map((section) =>
                section.id !== sectionId
                  ? section
                  : {
                      ...section,
                      administrations: section.administrations.map((a) =>
                        a.id !== administrationId
                          ? a
                          : {
                              ...a,
                              moyensHumains:
                                a.moyensHumains.length <= 1
                                  ? a.moyensHumains
                                  : a.moyensHumains.filter((m) => m.id !== moyenId),
                            }
                      ),
                    }
              ),
            }
      )
    );
  };

  const findSectionEntry = (predicate: (title: string) => boolean) => {
    for (const chapter of chapters) {
      for (const section of chapter.sections) {
        if (predicate(section.title)) {
          return { chapterId: chapter.id, sectionId: section.id, section };
        }
      }
    }
    return null;
  };

  useEffect(() => {
    const section2 = findSectionEntry(isMoyensHumainsSection);
    const section3 = findSectionEntry(isRoleIntervenantsSection);
    if (!section2 || !section3) return;
    const sourceAdmins = section2.section.administrations.map((a) => ({
      id: a.id,
      name: a.name,
      moyensHumains: a.moyensHumains.map((mh) => ({ nom: mh.nom })),
    }));
    const targetAdmins = section3.section.administrations.map((a) => ({
      id: a.id,
      name: a.name,
      moyensHumains: a.moyensHumains.map((mh) => ({ nom: mh.nom })),
    }));
    const same =
      sourceAdmins.length === targetAdmins.length &&
      sourceAdmins.every(
        (a, idx) =>
          a.id === targetAdmins[idx]?.id &&
          a.name === targetAdmins[idx]?.name &&
          a.moyensHumains.length === targetAdmins[idx]?.moyensHumains.length &&
          a.moyensHumains.every((mh, mhIdx) => mh.nom === targetAdmins[idx]?.moyensHumains[mhIdx]?.nom)
      );
    if (same) return;

    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id !== section3.chapterId
          ? chapter
          : {
              ...chapter,
              sections: chapter.sections.map((section) => {
                if (section.id !== section3.sectionId) return section;
                return {
                  ...section,
                  administrations: sourceAdmins.map((admin) => {
                    const existing = section.administrations.find((a) => a.id === admin.id);
                    return existing
                      ? {
                          ...existing,
                          name: admin.name,
                          moyensHumains: admin.moyensHumains.map((sourceMh) => {
                            const existingMh = existing.moyensHumains.find((m) => m.nom === sourceMh.nom);
                            return {
                              id: existingMh?.id ?? makeId(),
                              nom: sourceMh.nom,
                              description: existingMh?.description ?? "",
                            };
                          }),
                        }
                      : {
                          id: admin.id,
                          name: admin.name,
                          description: "",
                          rolePhaseEtudes: "",
                          rolePhaseChantier: "",
                          moyensHumains: admin.moyensHumains.map((mh) => ({
                            id: makeId(),
                            nom: mh.nom,
                            description: "",
                          })),
                        };
                  }),
                };
              }),
            }
      )
    );
  }, [chapters]);

  useEffect(() => {
    const source = findSectionEntry(isMoyensHumainsSection);
    const target = findSectionEntry(isImplicationsSection);
    if (!source || !target) return;
    const adminIds = source.section.administrations.map((a) => a.id);
    const nextMatrix = buildImplicationMatrix(adminIds, target.section.implicationMatrix);
    const same = JSON.stringify(nextMatrix) === JSON.stringify(target.section.implicationMatrix);
    if (same) return;
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id !== target.chapterId
          ? chapter
          : {
              ...chapter,
              sections: chapter.sections.map((section) =>
                section.id !== target.sectionId ? section : { ...section, implicationMatrix: nextMatrix }
              ),
            }
      )
    );
  }, [chapters]);

  useEffect(() => {
    const section3 = findSectionEntry(isRoleIntervenantsSection);
    if (!section3) return;
    const idsToLoad = section3.section.administrations
      .map((a) => a.id)
      .filter((id) => !loadedProfileIds.includes(id));
    if (idsToLoad.length === 0) return;

    const loadProfiles = async () => {
      for (const adminId of idsToLoad) {
        try {
          const res = await fetch(`${API_BASE}/memoire-technique/administrations/${adminId}/profile`);
          if (!res.ok) continue;
          const profile = await res.json();
          setChapters((prev) =>
            prev.map((chapter) =>
              chapter.id !== section3.chapterId
                ? chapter
                : {
                    ...chapter,
                    sections: chapter.sections.map((section) =>
                      section.id !== section3.sectionId
                        ? section
                        : {
                            ...section,
                            administrations: section.administrations.map((a) =>
                              a.id !== adminId
                                ? a
                                : {
                                    ...a,
                                    description: String(profile?.description ?? ""),
                                    rolePhaseEtudes: String(profile?.rolePhaseEtudes ?? ""),
                                    rolePhaseChantier: String(profile?.rolePhaseChantier ?? ""),
                                  }
                            ),
                          }
                    ),
                  }
            )
          );
          setLoadedProfileIds((prev) => (prev.includes(adminId) ? prev : [...prev, adminId]));
        } catch {
          // ignore
        }
      }
    };
    loadProfiles();
  }, [chapters, loadedProfileIds]);

  const saveRoleIntervenantsProfiles = async () => {
    const section3 = findSectionEntry(isRoleIntervenantsSection);
    if (!section3) return;
    for (const admin of section3.section.administrations) {
      await fetch(`${API_BASE}/memoire-technique/administrations/${admin.id}/profile`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          description: admin.description,
          rolePhaseEtudes: admin.rolePhaseEtudes,
          rolePhaseChantier: admin.rolePhaseChantier,
          moyensHumains: admin.moyensHumains.map((mh) => ({ nom: mh.nom, description: mh.description })),
        }),
      });
    }
  };

  const saveAdministrationProfile = async (
    admin: {
      id: number;
      description: string;
      rolePhaseEtudes: string;
      rolePhaseChantier: string;
      moyensHumains: { nom: string; description: string }[];
    }
  ) => {
    const res = await fetch(`${API_BASE}/memoire-technique/administrations/${admin.id}/profile`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        description: admin.description,
        rolePhaseEtudes: admin.rolePhaseEtudes,
        rolePhaseChantier: admin.rolePhaseChantier,
        moyensHumains: admin.moyensHumains,
      }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(typeof data?.detail === "string" ? data.detail : "Enregistrement impossible");
    }
  };

  const saveMoyensHumainsProfiles = async () => {
    const section2 = findSectionEntry(isMoyensHumainsSection);
    if (!section2) return;
    for (const admin of section2.section.administrations) {
      await saveAdministrationProfile({
        id: admin.id,
        description: admin.description,
        rolePhaseEtudes: admin.rolePhaseEtudes,
        rolePhaseChantier: admin.rolePhaseChantier,
        moyensHumains: admin.moyensHumains.map((mh) => ({ nom: mh.nom, description: mh.description })),
      });
    }
  };

  const togglePhaseForSection = (chapterId: string, sectionId: string, phase: string) => {
    setChapters((prev) =>
      prev.map((chapter) =>
        chapter.id !== chapterId
          ? chapter
          : {
              ...chapter,
              sections: chapter.sections.map((section) => {
                if (section.id !== sectionId) return section;
                const exists = section.selectedPhases.includes(phase);
                return {
                  ...section,
                  selectedPhases: exists
                    ? section.selectedPhases.filter((p) => p !== phase)
                    : [...section.selectedPhases, phase],
                };
              }),
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
      await saveMoyensHumainsProfiles();
      await saveRoleIntervenantsProfiles();
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
              {isLivrablesSection(section.title) && (
                <div className="memo-phase-picker">
                  <span className="memo-phase-label">Phases concernees (multi-selection, ordre de clic conserve)</span>
                  <div className="memo-phase-options">
                    {PHASE_OPTIONS.map((phase) => {
                      const selected = section.selectedPhases.includes(phase);
                      return (
                        <button
                          key={phase}
                          type="button"
                          className={`memo-phase-chip ${selected ? "selected" : ""}`}
                          onClick={() => togglePhaseForSection(chapter.id, section.id, phase)}
                        >
                          {phase}
                        </button>
                      );
                    })}
                  </div>
                  <div className="memo-phase-order">
                    <strong>Ordre de selection :</strong>{" "}
                    {section.selectedPhases.length > 0 ? section.selectedPhases.join(" → ") : "Aucune phase selectionnee"}
                  </div>
                </div>
              )}

              {isMoyensHumainsSection(section.title) && (
                <div className="memo-admin-box">
                  <span className="memo-phase-label">Administration (choisir existante ou en creer une nouvelle)</span>
                  <div className="memo-admin-mode">
                    <label className="memo-inline-check">
                      <input
                        type="radio"
                        checked={section.adminMode === "existing"}
                        onChange={() => updateSection(chapter.id, section.id, { adminMode: "existing" })}
                      />
                      Existant
                    </label>
                    <label className="memo-inline-check">
                      <input
                        type="radio"
                        checked={section.adminMode === "new"}
                        onChange={() => updateSection(chapter.id, section.id, { adminMode: "new" })}
                      />
                      Nouveau
                    </label>
                  </div>

                  {section.adminMode === "existing" ? (
                    <div className="memo-admin-add">
                      <select
                        value={section.existingAdministrationId ?? ""}
                        onChange={(e) =>
                          updateSection(chapter.id, section.id, {
                            existingAdministrationId: e.target.value ? Number(e.target.value) : null,
                          })
                        }
                      >
                        <option value="">Selectionner une administration</option>
                        {availableAdministrations.map((adm) => (
                          <option key={adm.id} value={adm.id}>
                            {adm.name}
                          </option>
                        ))}
                      </select>
                      <button type="button" onClick={() => addExistingAdministrationToSection(chapter.id, section.id)}>
                        Ajouter
                      </button>
                    </div>
                  ) : (
                    <div className="memo-admin-add">
                      <input
                        value={section.newAdministrationName}
                        onChange={(e) => updateSection(chapter.id, section.id, { newAdministrationName: e.target.value })}
                        placeholder="Nom de la nouvelle administration"
                      />
                      <button type="button" onClick={() => addNewAdministrationToSection(chapter.id, section.id)}>
                        Creer et ajouter
                      </button>
                    </div>
                  )}

                  <div className="memo-admin-list">
                    {section.administrations.map((adm) => (
                      <div key={`${section.id}-${adm.id}`} className="memo-admin-card">
                        <div className="memo-row">
                          <h4>{adm.name}</h4>
                          <button type="button" className="memo-btn-danger" onClick={() => removeAdministrationFromSection(chapter.id, section.id, adm.id)}>
                            Retirer
                          </button>
                          <button type="button" className="memo-btn-danger" onClick={() => deleteAdministrationFromDatabase(adm.id)}>
                            Supprimer base
                          </button>
                        </div>
                        <label>
                          Description
                          <textarea
                            value={adm.description}
                            onChange={(e) =>
                              setChapters((prev) =>
                                prev.map((c) =>
                                  c.id !== chapter.id
                                    ? c
                                    : {
                                        ...c,
                                        sections: c.sections.map((s) =>
                                          s.id !== section.id
                                            ? s
                                            : {
                                                ...s,
                                                administrations: s.administrations.map((a) =>
                                                  a.id !== adm.id ? a : { ...a, description: e.target.value }
                                                ),
                                              }
                                        ),
                                      }
                                )
                              )
                            }
                            rows={3}
                          />
                        </label>
                        {adm.moyensHumains.map((mh) => (
                          <div key={mh.id} className="memo-human-card">
                            <input
                              value={mh.nom}
                              onChange={(e) =>
                                updateMoyenHumain(chapter.id, section.id, adm.id, mh.id, { nom: e.target.value })
                              }
                              placeholder="Nom"
                            />
                            <textarea
                              value={mh.description}
                              onChange={(e) =>
                                updateMoyenHumain(chapter.id, section.id, adm.id, mh.id, { description: e.target.value })
                              }
                              placeholder="Description"
                              rows={3}
                            />
                            <button type="button" className="memo-icon-btn" onClick={() => removeMoyenHumain(chapter.id, section.id, adm.id, mh.id)}>
                              ×
                            </button>
                          </div>
                        ))}
                        <button type="button" className="memo-btn-soft" onClick={() => addMoyenHumain(chapter.id, section.id, adm.id)}>
                          + Ajouter un moyen humain
                        </button>
                        <button
                          type="button"
                          className="memo-btn-primary"
                          onClick={async () => {
                            try {
                              await saveAdministrationProfile({
                                id: adm.id,
                                description: adm.description,
                                rolePhaseEtudes: adm.rolePhaseEtudes,
                                rolePhaseChantier: adm.rolePhaseChantier,
                                moyensHumains: adm.moyensHumains.map((mh) => ({ nom: mh.nom, description: mh.description })),
                              });
                            } catch (err) {
                              setError(err instanceof Error ? err.message : "Erreur d'enregistrement");
                            }
                          }}
                        >
                          Enregistrer
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {isRoleIntervenantsSection(section.title) && (
                <div className="memo-admin-box">
                  <span className="memo-phase-label">Administrations pre-remplies depuis le chapitre 2</span>
                  <div className="memo-admin-list">
                    {section.administrations.map((adm) => (
                      <div key={`${section.id}-role-${adm.id}`} className="memo-admin-card">
                        <h4>{adm.name}</h4>
                        <label>
                          Description
                          <textarea
                            value={adm.description}
                            onChange={(e) =>
                              setChapters((prev) =>
                                prev.map((c) =>
                                  c.id !== chapter.id
                                    ? c
                                    : {
                                        ...c,
                                        sections: c.sections.map((s) =>
                                          s.id !== section.id
                                            ? s
                                            : {
                                                ...s,
                                                administrations: s.administrations.map((a) =>
                                                  a.id !== adm.id ? a : { ...a, description: e.target.value }
                                                ),
                                              }
                                        ),
                                      }
                                )
                              )
                            }
                            rows={3}
                          />
                        </label>
                        <label>
                          Role en phase etude
                          <textarea
                            value={adm.rolePhaseEtudes}
                            onChange={(e) =>
                              setChapters((prev) =>
                                prev.map((c) =>
                                  c.id !== chapter.id
                                    ? c
                                    : {
                                        ...c,
                                        sections: c.sections.map((s) =>
                                          s.id !== section.id
                                            ? s
                                            : {
                                                ...s,
                                                administrations: s.administrations.map((a) =>
                                                  a.id !== adm.id ? a : { ...a, rolePhaseEtudes: e.target.value }
                                                ),
                                              }
                                        ),
                                      }
                                )
                              )
                            }
                            rows={3}
                          />
                        </label>
                        <label>
                          Role en phase chantier
                          <textarea
                            value={adm.rolePhaseChantier}
                            onChange={(e) =>
                              setChapters((prev) =>
                                prev.map((c) =>
                                  c.id !== chapter.id
                                    ? c
                                    : {
                                        ...c,
                                        sections: c.sections.map((s) =>
                                          s.id !== section.id
                                            ? s
                                            : {
                                                ...s,
                                                administrations: s.administrations.map((a) =>
                                                  a.id !== adm.id ? a : { ...a, rolePhaseChantier: e.target.value }
                                                ),
                                              }
                                        ),
                                      }
                                )
                              )
                            }
                            rows={3}
                          />
                        </label>

                        {adm.moyensHumains.map((mh) => (
                          <div key={mh.id} className="memo-human-card">
                            <input
                              value={mh.nom}
                              onChange={(e) =>
                                updateMoyenHumain(chapter.id, section.id, adm.id, mh.id, { nom: e.target.value })
                              }
                              placeholder="Nom"
                            />
                            <textarea
                              value={mh.description}
                              onChange={(e) =>
                                updateMoyenHumain(chapter.id, section.id, adm.id, mh.id, { description: e.target.value })
                              }
                              placeholder="Description"
                              rows={3}
                            />
                            <button type="button" className="memo-icon-btn" onClick={() => removeMoyenHumain(chapter.id, section.id, adm.id, mh.id)}>
                              ×
                            </button>
                          </div>
                        ))}
                        <button type="button" className="memo-btn-soft" onClick={() => addMoyenHumain(chapter.id, section.id, adm.id)}>
                          + Ajouter un moyen humain
                        </button>
                        <button
                          type="button"
                          className="memo-btn-primary"
                          onClick={async () => {
                            try {
                              await saveAdministrationProfile({
                                id: adm.id,
                                description: adm.description,
                                rolePhaseEtudes: adm.rolePhaseEtudes,
                                rolePhaseChantier: adm.rolePhaseChantier,
                                moyensHumains: adm.moyensHumains.map((mh) => ({ nom: mh.nom, description: mh.description })),
                              });
                            } catch (err) {
                              setError(err instanceof Error ? err.message : "Erreur d'enregistrement");
                            }
                          }}
                        >
                          Enregistrer
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {isImplicationsSection(section.title) && (
                <div className="memo-admin-box">
                  <span className="memo-phase-label">
                    Tableau des implications (cases combinables P, C et/ou E) avec colonnes basées sur les Administrations.
                  </span>
                  <div className="memo-table-scroll">
                    <table className="memo-table memo-implication-table">
                      <thead>
                        <tr>
                          <th>
                            E : Execute la mission selon sa competence.<br />
                            P : Participe selon sa competence.<br />
                            C : Coordonne, realise compte rendu de reunion et synthese de la phase.
                          </th>
                          {(findSectionEntry(isMoyensHumainsSection)?.section.administrations ?? []).map((admin) => (
                            <th key={`head-admin-${admin.id}`}>{admin.name}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {section.implicationMatrix.map((row) => (
                          <tr key={`row-${section.id}-${row.label}`}>
                            <td>{row.label}</td>
                            {(findSectionEntry(isMoyensHumainsSection)?.section.administrations ?? []).map((admin) => {
                              const key = String(admin.id);
                              const selected = row.valuesByAdmin[key] ?? [];
                              return (
                                <td key={`cell-${section.id}-${row.label}-${admin.id}`}>
                                  <div className="memo-implication-cell">
                                    {(["P", "C", "E"] as const).map((v) => (
                                      <label key={`${row.label}-${admin.id}-${v}`} className="memo-inline-check">
                                        <input
                                          type="checkbox"
                                          checked={selected.includes(v)}
                                          onChange={() =>
                                            toggleImplicationValue(chapter.id, section.id, row.label, admin.id, v)
                                          }
                                        />
                                        {v}
                                      </label>
                                    ))}
                                  </div>
                                </td>
                              );
                            })}
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
