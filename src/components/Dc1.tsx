import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import type { Question } from "../App";
import { normalizeNewlines, sanitizeKey } from "../utils";

type DataItem = { keyword: string; answer: string };

type CandidateInfo = {
  nomCommercialDenomination: string;
  adressesPostaleSiege: string;
  adresseElectronique: string;
  telephoneTelecopie: string;
  siretOuIdentification: string;
};

type ObjetCandidatureChoice = "non_allotissement" | "tous_lots" | "lots_determines";

type PresentationType = "seul" | "groupement";
type GroupementType = "conjoint" | "solidaire";
type MandataireSolidaire = "oui" | "non";

type GroupementRow = { lotNumero: string; identification: string; prestations: string };
type SavedMember = { id: number; lotNumero: string; identification: string; prestations: string; created_at?: string };
type SavedMandataire = CandidateInfo & { id: number; created_at?: string };
type Dc1Props = { questions?: Question[] };

const API_BASE = "http://127.0.0.1:8011";

function Dc1({ questions: questionsProp = [] }: Dc1Props) {
  const [items, setItems] = useState<DataItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);
  const [creating, setCreating] = useState(false);
  const [createDone, setCreateDone] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [candidate, setCandidate] = useState<CandidateInfo>({
    nomCommercialDenomination: "",
    adressesPostaleSiege: "",
    adresseElectronique: "",
    telephoneTelecopie: "",
    siretOuIdentification: "",
  });
  const [objetCandidature, setObjetCandidature] = useState<ObjetCandidatureChoice | "">("");
  const [lotNumero, setLotNumero] = useState("");
  const [intituleLots, setIntituleLots] = useState("");
  const [presentationType, setPresentationType] = useState<PresentationType | "">("");
  const [groupementType, setGroupementType] = useState<GroupementType | "">("");
  const [mandataireSolidaire, setMandataireSolidaire] = useState<MandataireSolidaire | "">("");
  const [groupementRows, setGroupementRows] = useState<GroupementRow[]>([
    { lotNumero: "", identification: "", prestations: "" },
  ]);
  const [savedMembers, setSavedMembers] = useState<SavedMember[]>([]);
  // Module F - Engagements
  const [f1ExclusionChecked, setF1ExclusionChecked] = useState(false);
  const [f2AdresseInternet, setF2AdresseInternet] = useState("");
  const [f2RenseignementsAcces, setF2RenseignementsAcces] = useState("");
  const [f3FormulaireDC2, setF3FormulaireDC2] = useState(false);
  const [f3DocumentsCapacites, setF3DocumentsCapacites] = useState(false);
  // Module G - Mandataire (en cas de groupement)
  const [mandataire, setMandataire] = useState<CandidateInfo>({
    nomCommercialDenomination: "",
    adressesPostaleSiege: "",
    adresseElectronique: "",
    telephoneTelecopie: "",
    siretOuIdentification: "",
  });
  const [savedMandataires, setSavedMandataires] = useState<SavedMandataire[]>([]);

  const questions: Question[] = questionsProp.length > 0
    ? questionsProp
    : (() => {
        try {
          const raw = sessionStorage.getItem("ragQuestions");
          return raw ? (JSON.parse(raw) as Question[]) : [];
        } catch {
          return [];
        }
      })();

  // Charger les 5 derniers éléments de data
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
            return {
              keyword: normalizeNewlines(String(el[0] ?? "")),
              answer: normalizeNewlines(String(el[1] ?? "")),
            };
          }
          return {
            keyword: normalizeNewlines(String(el.keyword ?? "")),
            answer: normalizeNewlines(String(el.answer ?? "")),
          };
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

  // Charger les infos de présentation du candidat stockées précédemment
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("dc1Candidate");
      if (!raw) return;
      const parsed = JSON.parse(raw) as Partial<CandidateInfo>;
      setCandidate((prev) => ({ ...prev, ...parsed }));
    } catch {
      // ignore
    }
  }, []);

  // Charger l'objet de la candidature (C)
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("dc1ObjetCandidature");
      if (!raw) return;
      const parsed = JSON.parse(raw) as {
        objetCandidature?: ObjetCandidatureChoice;
        lotNumero?: string;
        intituleLots?: string;
      };
      if (parsed.objetCandidature)
        setObjetCandidature(parsed.objetCandidature);
      if (parsed.lotNumero != null) setLotNumero(parsed.lotNumero);
      if (parsed.intituleLots != null) setIntituleLots(parsed.intituleLots);
    } catch {
      // ignore
    }
  }, []);

  // Charger la présentation du candidat (D)
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("dc1Presentation");
      if (!raw) return;
      const parsed = JSON.parse(raw) as {
        presentationType?: PresentationType;
        groupementType?: GroupementType;
        mandataireSolidaire?: MandataireSolidaire;
      };
      if (parsed.presentationType) setPresentationType(parsed.presentationType);
      if (parsed.groupementType) setGroupementType(parsed.groupementType);
      if (parsed.mandataireSolidaire) setMandataireSolidaire(parsed.mandataireSolidaire);
    } catch {
      // ignore
    }
  }, []);

  // Charger le module F (engagements) et G (mandataire)
  useEffect(() => {
    try {
      const rawF = sessionStorage.getItem("dc1Engagements");
      if (rawF) {
        const f = JSON.parse(rawF) as {
          f1ExclusionChecked?: boolean;
          f2AdresseInternet?: string;
          f2RenseignementsAcces?: string;
          f3FormulaireDC2?: boolean;
          f3DocumentsCapacites?: boolean;
        };
        if (f.f1ExclusionChecked != null) setF1ExclusionChecked(f.f1ExclusionChecked);
        if (f.f2AdresseInternet != null) setF2AdresseInternet(f.f2AdresseInternet);
        if (f.f2RenseignementsAcces != null) setF2RenseignementsAcces(f.f2RenseignementsAcces);
        if (f.f3FormulaireDC2 != null) setF3FormulaireDC2(f.f3FormulaireDC2);
        if (f.f3DocumentsCapacites != null) setF3DocumentsCapacites(f.f3DocumentsCapacites);
      }
      const rawG = sessionStorage.getItem("dc1Mandataire");
      if (rawG) {
        const g = JSON.parse(rawG) as Partial<CandidateInfo>;
        setMandataire((prev) => ({ ...prev, ...g }));
      }
    } catch {
      // ignore
    }
  }, []);

  // Charger les membres enregistrés (API) et le module E (sessionStorage)
  useEffect(() => {
    const fetchMembers = async () => {
      try {
        const res = await fetch(`${API_BASE}/members`);
        if (res.ok) {
          const data = await res.json();
          setSavedMembers(Array.isArray(data) ? data : []);
        }
      } catch {
        // ignore
      }
    };
    const fetchMandataires = async () => {
      try {
        const res = await fetch(`${API_BASE}/mandataires`);
        if (res.ok) {
          const data = await res.json();
          setSavedMandataires(Array.isArray(data) ? data : []);
        }
      } catch {
        // ignore
      }
    };
    fetchMembers();
    fetchMandataires();
  }, []);
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("dc1GroupementRows");
      if (!raw) return;
      const parsed = JSON.parse(raw) as GroupementRow[];
      if (Array.isArray(parsed) && parsed.length > 0) {
        setGroupementRows(parsed);
      }
    } catch {
      // ignore
    }
  }, []);

  const handleChange = (index: number, field: "keyword" | "answer", value: string) => {
    setItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, [field]: value } : item))
    );
    setSaved(false);
  };

  const getDc1Payload = () => {
    const toKeyValue = (item: DataItem | undefined) => {
      const kwRaw = normalizeNewlines(item?.keyword ?? "").trim();
      const kw = sanitizeKey(kwRaw);
      const ans = normalizeNewlines(item?.answer ?? "");
      return kw ? { [kw]: ans } : {};
    };
    const box = (checked: boolean) => (checked ? "☑" : "☐");
    const numberGroupementRows = () => {
      const out: Record<string, string> = {};
      groupementRows.forEach((row, idx) => {
        const n = idx + 1;
        out[`lotNumero_${n}`] = row.lotNumero ?? "";
        // clé demandée : "identifications" (avec s)
        out[`identifications_${n}`] = row.identification ?? "";
        out[`prestations_${n}`] = row.prestations ?? "";
      });
      return out;
    };
    return {
    moduleA: toKeyValue(items[0]),
    moduleB: toKeyValue(items[1]),
    moduleC: {
      objetCandidature: {
        non_allotissement: box(objetCandidature === "non_allotissement"),
        tous_lots: box(objetCandidature === "tous_lots"),
        lots_determines: box(objetCandidature === "lots_determines"),
      },
      lotNumero,
      intituleLots,
    },
    moduleD: {
      presentation: {
        seul: box(presentationType === "seul"),
        groupement: box(presentationType === "groupement"),
      },
      groupementType: {
        conjoint: box(groupementType === "conjoint"),
        solidaire: box(groupementType === "solidaire"),
      },
      mandataireSolidaire: {
        non: box(mandataireSolidaire === "non"),
        oui: box(mandataireSolidaire === "oui"),
      },
      candidate,
    },
    moduleE: numberGroupementRows(),
    moduleF: {
      f1ExclusionChecked: box(f1ExclusionChecked),
      f2AdresseInternet,
      f2RenseignementsAcces,
      f3FormulaireDC2: box(f3FormulaireDC2),
      f3DocumentsCapacites: box(f3DocumentsCapacites),
    },
    moduleG: { mandataire },
  };
  };

  const handleCreateDc1 = async () => {
    const raw = sessionStorage.getItem("ragData");
    try {
      if (raw) {
        const parsed = JSON.parse(raw) as unknown[];
        const list = Array.isArray(parsed) ? parsed : [];
        const head = list.slice(0, -items.length);
        const tail = items.map((i) => [i.keyword, i.answer] as [string, string]);
        sessionStorage.setItem("ragData", JSON.stringify([...head, ...tail]));
      } else {
        sessionStorage.setItem(
          "ragData",
          JSON.stringify(items.map((i) => [i.keyword, i.answer]))
        );
      }
    } catch {
      sessionStorage.setItem(
        "ragData",
        JSON.stringify(items.map((i) => [i.keyword, i.answer]))
      );
    }
    sessionStorage.setItem("dc1Candidate", JSON.stringify(candidate));
    sessionStorage.setItem(
      "dc1ObjetCandidature",
      JSON.stringify({ objetCandidature, lotNumero, intituleLots })
    );
    sessionStorage.setItem(
      "dc1Presentation",
      JSON.stringify({
        presentationType,
        groupementType,
        mandataireSolidaire,
      })
    );
    sessionStorage.setItem("dc1GroupementRows", JSON.stringify(groupementRows));
    sessionStorage.setItem(
      "dc1Engagements",
      JSON.stringify({
        f1ExclusionChecked,
        f2AdresseInternet,
        f2RenseignementsAcces,
        f3FormulaireDC2,
        f3DocumentsCapacites,
      })
    );
    sessionStorage.setItem("dc1Mandataire", JSON.stringify(mandataire));

    setCreating(true);
    setCreateDone(false);
    try {
      const res = await fetch(`${API_BASE}/dc1`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(getDc1Payload()),
      });
      if (res.ok) {
        setSaved(true);
        setCreateDone(true);
      }
    } catch {
      // ignore
    } finally {
      setCreating(false);
    }
  };

  const addGroupementRow = () => {
    setGroupementRows((prev) => [...prev, { lotNumero: "", identification: "", prestations: "" }]);
    setSaved(false);
  };
  const removeGroupementRow = (index: number) => {
    if (groupementRows.length <= 1) return;
    setGroupementRows((prev) => prev.filter((_, i) => i !== index));
    setSaved(false);
  };
  const updateGroupementRow = (index: number, field: keyof GroupementRow, value: string) => {
    setGroupementRows((prev) =>
      prev.map((r, i) => (i === index ? { ...r, [field]: value } : r))
    );
    setSaved(false);
  };
  const handleSaveMemberToDb = async (index: number) => {
    const row = groupementRows[index];
    if (!row) return;
    try {
      const res = await fetch(`${API_BASE}/members`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lotNumero: row.lotNumero,
          identification: row.identification,
          prestations: row.prestations,
        }),
      });
      if (res.ok) {
        const created = await res.json();
        setSavedMembers((prev) => [...prev, created]);
      }
    } catch {
      // ignore
    }
  };
  const handleAddSavedMember = (m: SavedMember) => {
    setGroupementRows((prev) => [
      ...prev,
      { lotNumero: m.lotNumero, identification: m.identification, prestations: m.prestations },
    ]);
    setSaved(false);
  };
  const handleDeleteMember = async (id: number) => {
    try {
      const res = await fetch(`${API_BASE}/members/${id}`, { method: "DELETE" });
      if (res.ok) {
        setSavedMembers((prev) => prev.filter((m) => m.id !== id));
      }
    } catch {
      // ignore
    }
  };
  const handleSaveMandataireToDb = async () => {
    try {
      const res = await fetch(`${API_BASE}/mandataires`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(mandataire),
      });
      if (res.ok) {
        const created = await res.json();
        setSavedMandataires((prev) => [...prev, created]);
      }
    } catch {
      // ignore
    }
  };
  const handleLoadMandataire = (m: SavedMandataire) => {
    setMandataire({
      nomCommercialDenomination: m.nomCommercialDenomination,
      adressesPostaleSiege: m.adressesPostaleSiege,
      adresseElectronique: m.adresseElectronique,
      telephoneTelecopie: m.telephoneTelecopie,
      siretOuIdentification: m.siretOuIdentification,
    });
    setSaved(false);
  };
  const handleDeleteMandataire = async (id: number) => {
    try {
      const res = await fetch(`${API_BASE}/mandataires/${id}`, { method: "DELETE" });
      if (res.ok) {
        setSavedMandataires((prev) => prev.filter((m) => m.id !== id));
      }
    } catch {
      // ignore
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
      <div className="dc1-layout">
        <main className="dc1-main">
          <div className="dc1-main-header">
            <button
              type="button"
              className="dc1-sidebar-toggle"
              onClick={() => setSidebarOpen((o) => !o)}
              title={sidebarOpen ? "Masquer les Q/R" : "Afficher les Q/R"}
            >
              {sidebarOpen ? "◀ Masquer Q/R" : "▶ Afficher Q/R"}
            </button>
            <h1>DC1</h1>
          </div>

          {/* Modules A et B - mot-clé en guise de titre */}
          {items.slice(0, 2).map((item, index) => (
            <div key={index} className="dc1-module">
              <div className="dc1-module-title dc1-module-title-row">
                <span>{index === 0 ? "A-" : "B-"}</span>
                <input
                  type="text"
                  className="dc1-module-title-input"
                  value={item.keyword}
                  onChange={(e) => handleChange(index, "keyword", e.target.value)}
                  placeholder="Mot-clé"
                />
              </div>
              <div className="dc1-module-content">
                <label>
                  <span className="dc1-label">Réponse</span>
                  <textarea
                    value={item.answer}
                    onChange={(e) => handleChange(index, "answer", e.target.value)}
                    rows={3}
                  />
                </label>
              </div>
            </div>
          ))}

          {/* Module C - Objet de la candidature (cases à cocher) */}
          <div className="dc1-module dc1-module-objet">
            <h2 className="dc1-module-title">C - Objet de la candidature</h2>
            <p className="dc1-module-instruction">
              (Cocher la case correspondante.) La candidature est présentée :
            </p>
            <div className="dc1-checkbox-list">
              <label className="dc1-checkbox-row">
                <span className="dc1-checkbox">
                  {objetCandidature === "non_allotissement" ? "☑" : "☐"}
                </span>
                <input
                  type="radio"
                  name="objet"
                  checked={objetCandidature === "non_allotissement"}
                  onChange={() => { setObjetCandidature("non_allotissement"); setSaved(false); }}
                  className="dc1-checkbox-input"
                />
                <span className="dc1-checkbox-text">
                  pour le marché public (en cas de non allotissement) ;
                </span>
              </label>
              <label className="dc1-checkbox-row">
                <span className="dc1-checkbox">
                  {objetCandidature === "tous_lots" ? "☑" : "☐"}
                </span>
                <input
                  type="radio"
                  name="objet"
                  checked={objetCandidature === "tous_lots"}
                  onChange={() => { setObjetCandidature("tous_lots"); setSaved(false); }}
                  className="dc1-checkbox-input"
                />
                <span className="dc1-checkbox-text">
                  pour tous les lots de la procédure de passation du marché public ;
                </span>
              </label>
              <label className="dc1-checkbox-row">
                <span className="dc1-checkbox">
                  {objetCandidature === "lots_determines" ? "☑" : "☐"}
                </span>
                <input
                  type="radio"
                  name="objet"
                  checked={objetCandidature === "lots_determines"}
                  onChange={() => { setObjetCandidature("lots_determines"); setSaved(false); }}
                  className="dc1-checkbox-input"
                />
                <span className="dc1-checkbox-text">
                  pour le lot n° … ou les lots n° … de la procédure de passation du
                  marché public (en cas d'allotissement ; si les lots n'ont pas été
                  numérotés, indiquer ci-dessous l'intitulé du ou des lots tels
                  qu'ils figurent dans l'avis d'appel à la concurrence ou
                  l'invitation à confirmer l'intérêt).
                </span>
              </label>
            </div>
            {objetCandidature === "lots_determines" && (
              <div className="dc1-lots-fields">
                <label>
                  <span className="dc1-label">N° du lot ou des lots</span>
                  <input
                    type="text"
                    value={lotNumero}
                    onChange={(e) => { setLotNumero(e.target.value); setSaved(false); }}
                    placeholder="ex. 1 ou 1, 2, 3"
                  />
                </label>
                <label>
                  <span className="dc1-label">Intitulé du ou des lots (si non numérotés)</span>
                  <input
                    type="text"
                    value={intituleLots}
                    onChange={(e) => { setIntituleLots(e.target.value); setSaved(false); }}
                    placeholder="tel qu’il figure dans l’avis ou l’invitation"
                  />
                </label>
              </div>
            )}
          </div>

          {/* Module D - Présentation du candidat (cases à cocher) */}
          <div className="dc1-module dc1-module-presentation">
            <h2 className="dc1-module-title">D - Présentation du candidat</h2>
            <div className="dc1-checkbox-list">
              <label className="dc1-checkbox-row">
                <span className="dc1-checkbox">
                  {presentationType === "seul" ? "☑" : "☐"}
                </span>
                <input
                  type="radio"
                  name="presentation"
                  checked={presentationType === "seul"}
                  onChange={() => {
                    setPresentationType("seul");
                    setGroupementType("");
                    setMandataireSolidaire("");
                    setSaved(false);
                  }}
                  className="dc1-checkbox-input"
                />
                <span className="dc1-checkbox-text">
                  Le candidat se présente seul :
                </span>
              </label>
              <p className="dc1-module-hint">
                [Indiquer le nom commercial et la dénomination sociale du candidat
                individuel, les adresses de son établissement et de son siège social
                (si elle est différente de celle de l'établissement), son adresse
                électronique, ses numéros de téléphone et de télécopie et son numéro
                SIRET ; à défaut, un numéro d'identification européen ou international
                ou propre au pays d'origine du candidat.]
              </p>
              {presentationType === "seul" && (
                <div className="dc1-candidate-fields">
                  <label>
                    <span className="dc1-label">Nom commercial et dénomination sociale de l'unité ou de l'établissement qui exécutera la prestation :</span>
                    <input
                      type="text"
                      value={candidate.nomCommercialDenomination}
                      onChange={(e) => {
                        setCandidate((c) => ({ ...c, nomCommercialDenomination: e.target.value }));
                        setSaved(false);
                      }}
                    />
                  </label>
                  <label>
                    <span className="dc1-label">Adresses postale et du siège social (si elle est différente de l'adresse postale) :</span>
                    <input
                      type="text"
                      value={candidate.adressesPostaleSiege}
                      onChange={(e) => {
                        setCandidate((c) => ({ ...c, adressesPostaleSiege: e.target.value }));
                        setSaved(false);
                      }}
                    />
                  </label>
                  <label>
                    <span className="dc1-label">Adresse électronique :</span>
                    <input
                      type="email"
                      value={candidate.adresseElectronique}
                      onChange={(e) => {
                        setCandidate((c) => ({ ...c, adresseElectronique: e.target.value }));
                        setSaved(false);
                      }}
                    />
                  </label>
                  <label>
                    <span className="dc1-label">Numéros de téléphone et de télécopie :</span>
                    <input
                      type="text"
                      value={candidate.telephoneTelecopie}
                      onChange={(e) => {
                        setCandidate((c) => ({ ...c, telephoneTelecopie: e.target.value }));
                        setSaved(false);
                      }}
                    />
                  </label>
                  <label>
                    <span className="dc1-label">Numéro SIRET, à défaut numéro d'identification européen ou international ou propre au pays d'origine :</span>
                    <input
                      type="text"
                      value={candidate.siretOuIdentification}
                      onChange={(e) => {
                        setCandidate((c) => ({ ...c, siretOuIdentification: e.target.value }));
                        setSaved(false);
                      }}
                    />
                  </label>
                </div>
              )}

              <label className="dc1-checkbox-row">
                <span className="dc1-checkbox">
                  {presentationType === "groupement" ? "☑" : "☐"}
                </span>
                <input
                  type="radio"
                  name="presentation"
                  checked={presentationType === "groupement"}
                  onChange={() => {
                    setPresentationType("groupement");
                    setSaved(false);
                  }}
                  className="dc1-checkbox-input"
                />
                <span className="dc1-checkbox-text">
                  Le candidat est un groupement d'entreprises :
                </span>
              </label>
              {presentationType === "groupement" && (
                <>
                  <div className="dc1-sub-options">
                    <span className="dc1-ou">OU</span>
                    <label className="dc1-checkbox-row dc1-inline">
                      <span className="dc1-checkbox">
                        {groupementType === "conjoint" ? "☑" : "☐"}
                      </span>
                      <input
                        type="radio"
                        name="groupement"
                        checked={groupementType === "conjoint"}
                        onChange={() => {
                          setGroupementType("conjoint");
                          setSaved(false);
                        }}
                        className="dc1-checkbox-input"
                      />
                      <span className="dc1-checkbox-text">conjoint</span>
                    </label>
                    <label className="dc1-checkbox-row dc1-inline">
                      <span className="dc1-checkbox">
                        {groupementType === "solidaire" ? "☑" : "☐"}
                      </span>
                      <input
                        type="radio"
                        name="groupement"
                        checked={groupementType === "solidaire"}
                        onChange={() => {
                          setGroupementType("solidaire");
                          setMandataireSolidaire("");
                          setSaved(false);
                        }}
                        className="dc1-checkbox-input"
                      />
                      <span className="dc1-checkbox-text">solidaire</span>
                    </label>
                  </div>
                  {groupementType === "conjoint" && (
                    <div className="dc1-sub-options dc1-mandataire">
                      <span className="dc1-checkbox-text">
                        En cas de groupement conjoint, le mandataire est solidaire :
                      </span>
                      <span className="dc1-ou">OU</span>
                      <label className="dc1-checkbox-row dc1-inline">
                        <span className="dc1-checkbox">
                          {mandataireSolidaire === "non" ? "☑" : "☐"}
                        </span>
                        <input
                          type="radio"
                          name="mandataire"
                          checked={mandataireSolidaire === "non"}
                          onChange={() => {
                            setMandataireSolidaire("non");
                            setSaved(false);
                          }}
                          className="dc1-checkbox-input"
                        />
                        <span className="dc1-checkbox-text">Non</span>
                      </label>
                      <label className="dc1-checkbox-row dc1-inline">
                        <span className="dc1-checkbox">
                          {mandataireSolidaire === "oui" ? "☑" : "☐"}
                        </span>
                        <input
                          type="radio"
                          name="mandataire"
                          checked={mandataireSolidaire === "oui"}
                          onChange={() => {
                            setMandataireSolidaire("oui");
                            setSaved(false);
                          }}
                          className="dc1-checkbox-input"
                        />
                        <span className="dc1-checkbox-text">Oui</span>
                      </label>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Module E - Identification des membres du groupement */}
          <div className="dc1-module dc1-module-groupement">
            <h2 className="dc1-module-title">
              E - Identification des membres du groupement et répartition des prestations
            </h2>
            <p className="dc1-module-instruction">
              (Tous les membres du groupement remplissent le tableau ci-dessous. En cas de
              groupement conjoint, les membres du groupement indiquent également dans ce tableau la
              répartition des prestations que chacun d&apos;entre eux s&apos;engage à exécuter. Ajouter
              autant de lignes que nécessaires.)
            </p>
            <div className="dc1-groupement-load">
              <label>
                <span className="dc1-label">
                  {savedMembers.length > 0
                    ? "Ajouter un membre enregistré :"
                    : "Aucun membre enregistré pour le moment."}
                </span>
                {savedMembers.length > 0 && (
                  <select
                    className="dc1-select-groupement"
                    value=""
                    onChange={(e) => {
                      const id = e.target.value ? parseInt(e.target.value, 10) : 0;
                      if (id) {
                        const m = savedMembers.find((x) => x.id === id);
                        if (m) handleAddSavedMember(m);
                      }
                      e.target.value = "";
                    }}
                  >
                    <option value="">— Sélectionner —</option>
                    {savedMembers.map((m) => {
                      const label = m.identification
                        ? (m.identification.length > 35 ? m.identification.slice(0, 35) + "…" : m.identification)
                        : "(vide)";
                      return (
                        <option key={m.id} value={m.id}>
                          Lot {m.lotNumero || "—"} · {label} · {new Date(m.created_at || "").toLocaleDateString("fr-FR")}
                        </option>
                      );
                    })}
                  </select>
                )}
              </label>
              {savedMembers.length > 0 && (
                <ul className="dc1-saved-members-list">
                  {savedMembers.map((m) => (
                    <li key={m.id} className="dc1-saved-member-item">
                      <span className="dc1-saved-member-label">
                        Lot {m.lotNumero || "—"} · {(m.identification || "(vide)").slice(0, 40)}
                        {(m.identification?.length ?? 0) > 40 ? "…" : ""}
                      </span>
                      <button
                        type="button"
                        className="dc1-btn-delete-member"
                        onClick={() => handleDeleteMember(m.id)}
                        title="Supprimer ce membre de la base"
                      >
                        Supprimer
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="dc1-module-content">
              <div className="dc1-table-wrap">
                <table className="dc1-table">
                  <thead>
                    <tr>
                      <th className="dc1-th-lot">N° du Lot</th>
                      <th className="dc1-th-id">
                        Nom commercial et dénomination sociale, adresse de l&apos;établissement (*),
                        adresse électronique, numéros de téléphone et de télécopie, numéro SIRET des
                        membres du groupement (***)
                      </th>
                      <th className="dc1-th-presta">
                        Prestations exécutées par les membres du groupement (**)
                      </th>
                      <th className="dc1-th-actions">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {groupementRows.map((row, index) => (
                      <tr key={index}>
                        <td>
                          <input
                            type="text"
                            value={row.lotNumero}
                            onChange={(e) => updateGroupementRow(index, "lotNumero", e.target.value)}
                            placeholder="ex. 1"
                          />
                        </td>
                        <td>
                          <textarea
                            value={row.identification}
                            onChange={(e) =>
                              updateGroupementRow(index, "identification", e.target.value)
                            }
                            rows={2}
                            placeholder="Nom, adresse, email, tél, SIRET..."
                          />
                        </td>
                        <td>
                          <textarea
                            value={row.prestations}
                            onChange={(e) =>
                              updateGroupementRow(index, "prestations", e.target.value)
                            }
                            rows={2}
                            placeholder="Prestations exécutées..."
                          />
                        </td>
                        <td>
                          <div className="dc1-row-actions">
                            <button
                              type="button"
                              className="dc1-btn-save-member"
                              onClick={() => handleSaveMemberToDb(index)}
                              title="Enregistrer ce membre"
                            >
                              Enregistrer
                            </button>
                            <button
                              type="button"
                              className="dc1-btn-remove"
                              onClick={() => removeGroupementRow(index)}
                              disabled={groupementRows.length <= 1}
                              title="Supprimer la ligne"
                            >
                              ✕
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="dc1-groupement-actions">
                <button type="button" className="dc1-btn-add" onClick={addGroupementRow}>
                  + Ajouter une ligne
                </button>
              </div>
            </div>
          </div>

          {/* Module F - Engagements du candidat ou de chaque membre du groupement */}
          <div className="dc1-module dc1-module-engagements">
            <h2 className="dc1-module-title">
              F - Engagements du candidat individuel ou de chaque membre du groupement
            </h2>
            <div className="dc1-module-content">
              <div className="dc1-f-section">
                <h3 className="dc1-f-subtitle">F1 - Exclusions de la procédure</h3>
                <p className="dc1-module-instruction dc1-f-text">
                  Le candidat individuel ou chaque membre du groupement déclare sur l&apos;honneur ne pas
                  se trouver dans un des cas d&apos;exclusion mentionnés aux articles L. 2141-1 à L. 2141-5
                  et L. 2141-7 à L. 2141-10 du code de la commande publique (marchés de défense ou de
                  sécurité).
                </p>
                <p className="dc1-module-hint dc1-f-note">
                  (*) Si un opérateur économique entre, au cours de la procédure de passation du marché,
                  dans un des cas d&apos;exclusion mentionnés (notamment L. 2341-1 à L. 2341-3), il doit
                  en informer immédiatement l&apos;acheteur de ce changement de situation.
                </p>
                <label className="dc1-checkbox-row">
                  <span className="dc1-checkbox">{f1ExclusionChecked ? "☑" : "☐"}</span>
                  <input
                    type="checkbox"
                    checked={f1ExclusionChecked}
                    onChange={(e) => { setF1ExclusionChecked(e.target.checked); setSaved(false); }}
                    className="dc1-checkbox-input"
                  />
                  <span className="dc1-checkbox-text">
                    Afin d&apos;attester que le candidat individuel, ou chaque membre du groupement,
                    n&apos;est pas dans un de ces cas d&apos;exclusion, cocher la case suivante :
                  </span>
                </label>
              </div>

              <div className="dc1-f-section">
                <h3 className="dc1-f-subtitle">F2 - Documents de preuve disponibles en ligne</h3>
                <p className="dc1-module-instruction dc1-f-text">
                  (Articles R. 2343-14 ou R. 2343-15 du code de la commande publique — lorsque
                  l&apos;acheteur a autorisé les candidats à ne pas joindre ces documents à l&apos;appui
                  de leur candidature.)
                </p>
                <div className="dc1-lots-fields">
                  <label>
                    <span className="dc1-label">Adresse internet :</span>
                    <input
                      type="url"
                      value={f2AdresseInternet}
                      onChange={(e) => { setF2AdresseInternet(e.target.value); setSaved(false); }}
                      placeholder="https://..."
                    />
                  </label>
                  <label>
                    <span className="dc1-label">Renseignements nécessaires pour y accéder :</span>
                    <input
                      type="text"
                      value={f2RenseignementsAcces}
                      onChange={(e) => { setF2RenseignementsAcces(e.target.value); setSaved(false); }}
                      placeholder="(Si identiques à une section précédente, s’y référer)"
                    />
                  </label>
                </div>
              </div>

              <div className="dc1-f-section">
                <h3 className="dc1-f-subtitle">F3 - Capacités</h3>
                <p className="dc1-module-instruction dc1-f-text">
                  Le candidat individuel ou les membres du groupement produisent les documents
                  permettant de vérifier les critères d&apos;aptitude professionnelle, de capacité
                  économique et financière et de capacité technique et professionnelle.
                </p>
                <label className="dc1-checkbox-row">
                  <span className="dc1-checkbox">{f3FormulaireDC2 ? "☑" : "☐"}</span>
                  <input
                    type="checkbox"
                    checked={f3FormulaireDC2}
                    onChange={(e) => { setF3FormulaireDC2(e.target.checked); setSaved(false); }}
                    className="dc1-checkbox-input"
                  />
                  <span className="dc1-checkbox-text">le formulaire DC2.</span>
                </label>
                <label className="dc1-checkbox-row">
                  <span className="dc1-checkbox">{f3DocumentsCapacites ? "☑" : "☐"}</span>
                  <input
                    type="checkbox"
                    checked={f3DocumentsCapacites}
                    onChange={(e) => { setF3DocumentsCapacites(e.target.checked); setSaved(false); }}
                    className="dc1-checkbox-input"
                  />
                  <span className="dc1-checkbox-text">
                    les documents établissant ses capacités, tels que demandés dans les documents de
                    la consultation (*).
                  </span>
                </label>
                <p className="dc1-module-hint dc1-f-note">
                  (*) Pour les marchés publics de défense ou de sécurité, certains justificatifs
                  doivent être fournis au stade de la candidature ; consulter les pièces. Pour les
                  autres marchés, le candidat fournit les informations ; il n&apos;a pas l&apos;obligation
                  légale de joindre les justificatifs s&apos;il choisit de ne pas le faire pour remplir
                  les conditions de participation.
                </p>
              </div>
            </div>
          </div>

          {/* Module G - Désignation du mandataire (en cas de groupement) */}
          <div className="dc1-module dc1-module-mandataire">
            <h2 className="dc1-module-title">
              G - Désignation du mandataire (en cas de groupement)
            </h2>
            <div className="dc1-module-content">
              <p className="dc1-module-instruction dc1-f-text">
                En cas de groupement, identification du mandataire du groupement.
              </p>
              <div className="dc1-groupement-load">
                <label>
                  <span className="dc1-label">
                    {savedMandataires.length > 0
                      ? "Charger un mandataire enregistré :"
                      : "Aucun mandataire enregistré pour le moment."}
                  </span>
                  {savedMandataires.length > 0 && (
                    <select
                      className="dc1-select-groupement"
                      value=""
                      onChange={(e) => {
                        const id = e.target.value ? parseInt(e.target.value, 10) : 0;
                        if (id) {
                          const m = savedMandataires.find((x) => x.id === id);
                          if (m) handleLoadMandataire(m);
                        }
                        e.target.value = "";
                      }}
                    >
                      <option value="">— Sélectionner —</option>
                      {savedMandataires.map((m) => {
                        const label = m.nomCommercialDenomination
                          ? (m.nomCommercialDenomination.length > 35
                              ? m.nomCommercialDenomination.slice(0, 35) + "…"
                              : m.nomCommercialDenomination)
                          : "(sans nom)";
                        return (
                          <option key={m.id} value={m.id}>
                            {label} · {new Date(m.created_at || "").toLocaleDateString("fr-FR")}
                          </option>
                        );
                      })}
                    </select>
                  )}
                </label>
                {savedMandataires.length > 0 && (
                  <ul className="dc1-saved-members-list">
                    {savedMandataires.map((m) => (
                      <li key={m.id} className="dc1-saved-member-item">
                        <span className="dc1-saved-member-label">
                          {m.nomCommercialDenomination || "(sans nom)"} · {m.adresseElectronique || ""}
                        </span>
                        <button
                          type="button"
                          className="dc1-btn-delete-member"
                          onClick={() => handleDeleteMandataire(m.id)}
                          title="Supprimer ce mandataire de la base"
                        >
                          Supprimer
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div className="dc1-candidate-fields">
                <label>
                  <span className="dc1-label">Nom commercial et dénomination sociale de l&apos;unité ou de l&apos;établissement qui exécutera la prestation :</span>
                  <input
                    type="text"
                    value={mandataire.nomCommercialDenomination}
                    onChange={(e) => {
                      setMandataire((c) => ({ ...c, nomCommercialDenomination: e.target.value }));
                      setSaved(false);
                    }}
                  />
                </label>
                <label>
                  <span className="dc1-label">Adresses postale et du siège social (si elle est différente de l&apos;adresse postale) :</span>
                  <input
                    type="text"
                    value={mandataire.adressesPostaleSiege}
                    onChange={(e) => {
                      setMandataire((c) => ({ ...c, adressesPostaleSiege: e.target.value }));
                      setSaved(false);
                    }}
                  />
                </label>
                <label>
                  <span className="dc1-label">Adresse électronique :</span>
                  <input
                    type="email"
                    value={mandataire.adresseElectronique}
                    onChange={(e) => {
                      setMandataire((c) => ({ ...c, adresseElectronique: e.target.value }));
                      setSaved(false);
                    }}
                  />
                </label>
                <label>
                  <span className="dc1-label">Numéros de téléphone et de télécopie :</span>
                  <input
                    type="text"
                    value={mandataire.telephoneTelecopie}
                    onChange={(e) => {
                      setMandataire((c) => ({ ...c, telephoneTelecopie: e.target.value }));
                      setSaved(false);
                    }}
                  />
                </label>
                <label>
                  <span className="dc1-label">Numéro SIRET, à défaut numéro d&apos;identification européen ou international ou propre au pays d&apos;origine :</span>
                  <input
                    type="text"
                    value={mandataire.siretOuIdentification}
                    onChange={(e) => {
                      setMandataire((c) => ({ ...c, siretOuIdentification: e.target.value }));
                      setSaved(false);
                    }}
                  />
                </label>
              </div>
              <div className="dc1-groupement-actions">
                <button
                  type="button"
                  className="dc1-btn-save-db"
                  onClick={handleSaveMandataireToDb}
                >
                  Enregistrer ce mandataire
                </button>
              </div>
            </div>
          </div>

          <div className="dc1-actions">
            <button
              type="button"
              className="dc1-save"
              onClick={handleCreateDc1}
              disabled={creating}
              title="Envoyer toutes les données DC1 au serveur"
            >
              {creating
                ? "Envoi…"
                : createDone
                  ? "✓ DC1 envoyé"
                  : `Créer DC1${saved ? "" : " *"}`
              }
            </button>
            <Link to="/results" className="dc1-back">
              ← Retour aux résultats
            </Link>
          </div>
        </main>

        {sidebarOpen && (
          <aside className="dc1-sidebar">
            <h2 className="dc1-sidebar-title">Questions / Réponses</h2>
            {questions.length === 0 ? (
              <p className="dc1-sidebar-empty">Aucune question en mémoire.</p>
            ) : (
              <ul className="dc1-sidebar-list">
                {questions.map((q, idx) => (
                  <li key={idx} className="dc1-sidebar-card">
                    <p className="dc1-sidebar-question">{q.question}</p>
                    <p className="dc1-sidebar-reponse">{normalizeNewlines(q.reponse)}</p>
                  </li>
                ))}
              </ul>
            )}
          </aside>
        )}
      </div>
    </section>
  );
}

export default Dc1;
