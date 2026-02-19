import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import type { Question } from "../App";
import { API_BASE } from "../config";
import { normalizeNewlines } from "../utils";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  question?: string;
  keyword?: string;
  rerank?: string;
  content: string;
};

type ModuleC1Data = {
  nomCommercialDenomination: string;
  adressesPostaleSiege: string;
  adresseElectronique: string;
  telephoneTelecopie: string;
  siretOuIdentification: string;
  formeJuridique: string;
  microPetiteMoyenneEntreprise: "oui" | "non" | "";
};

const initialC1: ModuleC1Data = {
  nomCommercialDenomination: "",
  adressesPostaleSiege: "",
  adresseElectronique: "",
  telephoneTelecopie: "",
  siretOuIdentification: "",
  formeJuridique: "",
  microPetiteMoyenneEntreprise: "",
};

type C2RowData = {
  isChecked: boolean;
  adresseInternet: string;
  renseignements: string;
};

const C2_STRUCTURE: {
  typeMarche: string;
  typeStructure: string;
}[] = [
  {
    typeMarche:
      "Marché réservé aux structures de l'insertion par l'activité économique et/ou aux structures du handicap (articles L. 2113-12, L. 2113-13 et L. 2113-14 du code de la commande publique)",
    typeStructure:
      "Structure d'insertion par l'activité économique (article L.5132-4 du code du travail) ou structure équivalente",
  },
  {
    typeMarche: "",
    typeStructure: "Entreprise adaptée (article L. 5213-13 du code du travail) ou structure équivalente",
  },
  {
    typeMarche: "",
    typeStructure:
      "Etablissement et service d'aide par le travail (articles L. 344-2 et s. du code de l'action sociale et des familles) ou structure équivalente",
  },
  {
    typeMarche:
      "Marché réservé aux entreprises de l'économie sociale et solidaire (article L. 2113-15 du code de la commande publique)",
    typeStructure:
      "Entreprise de l'économie sociale et solidaire (article 1e de la loi 2014-856 du 31 juillet 2014) ou structure équivalente",
  },
  {
    typeMarche: "Marché réservé pénitentiaire (article L. 2113-13-1 du code de la commande publique)",
    typeStructure:
      "Opérateur économique prévoyant d'exécuter le marché dans le cadre d'activités de production de biens et de services réalisés en établissement pénitentiaire",
  },
];

const initialC2Row = (): C2RowData => ({
  isChecked: false,
  adresseInternet: "",
  renseignements: "",
});

type ModuleC3Data = {
  nomListeOfficielle: string;
  referencesInscriptionClassification: string;
  adresseInternetCertificat: string;
  renseignementsAccesCertificat: string;
  declareSurHonneur: boolean;
};

const initialC3: ModuleC3Data = {
  nomListeOfficielle: "",
  referencesInscriptionClassification: "",
  adresseInternetCertificat: "",
  renseignementsAccesCertificat: "",
  declareSurHonneur: false,
};

type ModuleEData = {
  e1InscriptionRegistre: string;
  e2AutorisationOrganisation: string;
  e3AdressesInternet: string;
  e3RenseignementsAcces: string;
};

const initialE: ModuleEData = {
  e1InscriptionRegistre: "",
  e2AutorisationOrganisation: "",
  e3AdressesInternet: "",
  e3RenseignementsAcces: "",
};

type ExerciseF1Data = {
  du: string;
  au: string;
  chiffreAffairesGlobal: string;
  partChiffreAffaires: string;
};

type ModuleFData = {
  exercises: [ExerciseF1Data, ExerciseF1Data, ExerciseF1Data];
  dateCreationOuDebutActivite: string;
  f2AutresInfos: string;
  f3ResponsabiliteDecennale: boolean;
  f4AdresseInternet: string;
  f4RenseignementsAcces: string;
};

const initialExerciseF1 = (): ExerciseF1Data => ({
  du: "",
  au: "",
  chiffreAffairesGlobal: "",
  partChiffreAffaires: "",
});

const initialF: ModuleFData = {
  exercises: [
    initialExerciseF1(),
    initialExerciseF1(),
    initialExerciseF1(),
  ],
  dateCreationOuDebutActivite: "",
  f2AutresInfos: "",
  f3ResponsabiliteDecennale: false,
  f4AdresseInternet: "",
  f4RenseignementsAcces: "",
};

type ModuleGData = {
  g1Recapitulatif: string;
  g2AdresseInternet: string;
  g2RenseignementsAcces: string;
};

const initialG: ModuleGData = {
  g1Recapitulatif: "",
  g2AdresseInternet: "",
  g2RenseignementsAcces: "",
};

type HOperateurRow = {
  lotNumero: string;
  nomMembreGroupement: string;
  identification: string;
};

type SavedHOperateur = HOperateurRow & { id: number; created_at?: string };

type ModuleIData = {
  i1Contenu: string;
  i2AdresseInternet: string;
  i2RenseignementsAcces: string;
};

const initialI: ModuleIData = {
  i1Contenu: "",
  i2AdresseInternet: "",
  i2RenseignementsAcces: "",
};

function Dc2() {
  const [identificationAcheteur, setIdentificationAcheteur] = useState("");
  const [acheteurId, setAcheteurId] = useState("");
  const [moduleC1, setModuleC1] = useState<ModuleC1Data>(initialC1);
  const [moduleC2, setModuleC2] = useState<C2RowData[]>(() =>
    C2_STRUCTURE.map(() => initialC2Row())
  );
  const [moduleC3, setModuleC3] = useState<ModuleC3Data>(initialC3);
  const [moduleE, setModuleE] = useState<ModuleEData>(initialE);
  const [moduleF, setModuleF] = useState<ModuleFData>(initialF);
  const [moduleG, setModuleG] = useState<ModuleGData>(initialG);
  const [moduleHRows, setModuleHRows] = useState<HOperateurRow[]>([
    { lotNumero: "", nomMembreGroupement: "", identification: "" },
  ]);
  const [savedHOperateurs, setSavedHOperateurs] = useState<SavedHOperateur[]>([]);
  const [moduleI, setModuleI] = useState<ModuleIData>(initialI);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [keyword, setKeyword] = useState("");
  const [rerankQuestion, setRerankQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [createDone, setCreateDone] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const box = (checked: boolean) => (checked ? "☑" : "☐");

  const questions: Question[] = (() => {
    try {
      const raw = sessionStorage.getItem("ragQuestions");
      return raw ? (JSON.parse(raw) as Question[]) : [];
    } catch {
      return [];
    }
  })();

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

  // Préremplir depuis ragData (operationType, acheteurId)
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("ragData");
      if (!raw) return;
      const parsed = JSON.parse(raw) as unknown;
      const list = Array.isArray(parsed) ? parsed : [];
      for (const el of list) {
        const kw = Array.isArray(el) ? el[0] : (el as { keyword?: string })?.keyword;
        const ans = Array.isArray(el) ? el[1] : (el as { answer?: string })?.answer;
        if (kw === "acheteurId" && ans != null) {
          setIdentificationAcheteur(normalizeNewlines(String(ans)));
        }
        if (kw === "operationType" && ans != null) {
          setAcheteurId(normalizeNewlines(String(ans)));
        }
      }
    } catch {
      // ignore
    }
  }, []);

  const hasLoadedC1Ref = useRef(false);

  // Charger le module C1 (sessionStorage)
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("dc2ModuleC1");
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<ModuleC1Data>;
        setModuleC1((prev) => ({ ...initialC1, ...prev, ...parsed }));
      }
    } catch {
      // ignore
    }
    hasLoadedC1Ref.current = true;
  }, []);

  const updateC1 = (field: keyof ModuleC1Data, value: string | "oui" | "non") => {
    setModuleC1((prev) => ({ ...prev, [field]: value }));
  };

  useEffect(() => {
    if (!hasLoadedC1Ref.current) return;
    try {
      sessionStorage.setItem("dc2ModuleC1", JSON.stringify(moduleC1));
    } catch {
      // ignore
    }
  }, [moduleC1]);

  const hasLoadedC2Ref = useRef(false);
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("dc2ModuleC2");
      if (raw) {
        const parsed = JSON.parse(raw) as C2RowData[];
        if (Array.isArray(parsed) && parsed.length === C2_STRUCTURE.length) {
          setModuleC2(parsed);
        }
      }
    } catch {
      // ignore
    }
    hasLoadedC2Ref.current = true;
  }, []);

  useEffect(() => {
    if (!hasLoadedC2Ref.current) return;
    try {
      sessionStorage.setItem("dc2ModuleC2", JSON.stringify(moduleC2));
    } catch {
      // ignore
    }
  }, [moduleC2]);

  const updateC2 = (index: number, field: keyof C2RowData, value: boolean | string) => {
    setModuleC2((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], [field]: value };
      return next;
    });
  };

  const hasLoadedC3Ref = useRef(false);
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("dc2ModuleC3");
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<ModuleC3Data>;
        setModuleC3((prev) => ({ ...initialC3, ...prev, ...parsed }));
      }
    } catch {
      // ignore
    }
    hasLoadedC3Ref.current = true;
  }, []);

  useEffect(() => {
    if (!hasLoadedC3Ref.current) return;
    try {
      sessionStorage.setItem("dc2ModuleC3", JSON.stringify(moduleC3));
    } catch {
      // ignore
    }
  }, [moduleC3]);

  const updateC3 = (field: keyof ModuleC3Data, value: string | boolean) => {
    setModuleC3((prev) => ({ ...prev, [field]: value }));
  };

  const hasLoadedERef = useRef(false);
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("dc2ModuleE");
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<ModuleEData>;
        setModuleE((prev) => ({ ...initialE, ...prev, ...parsed }));
      }
    } catch {
      // ignore
    }
    hasLoadedERef.current = true;
  }, []);

  useEffect(() => {
    if (!hasLoadedERef.current) return;
    try {
      sessionStorage.setItem("dc2ModuleE", JSON.stringify(moduleE));
    } catch {
      // ignore
    }
  }, [moduleE]);

  const updateE = (field: keyof ModuleEData, value: string) => {
    setModuleE((prev) => ({ ...prev, [field]: value }));
  };

  const hasLoadedFRef = useRef(false);
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("dc2ModuleF");
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<ModuleFData>;
        if (parsed.exercises && Array.isArray(parsed.exercises) && parsed.exercises.length === 3) {
          setModuleF((prev) => ({
            ...initialF,
            ...prev,
            exercises: parsed.exercises as [ExerciseF1Data, ExerciseF1Data, ExerciseF1Data],
            dateCreationOuDebutActivite: parsed.dateCreationOuDebutActivite ?? prev.dateCreationOuDebutActivite,
          }));
        } else {
          setModuleF((prev) => ({ ...initialF, ...prev, ...parsed }));
        }
      }
    } catch {
      // ignore
    }
    hasLoadedFRef.current = true;
  }, []);

  useEffect(() => {
    if (!hasLoadedFRef.current) return;
    try {
      sessionStorage.setItem("dc2ModuleF", JSON.stringify(moduleF));
    } catch {
      // ignore
    }
  }, [moduleF]);

  const updateFExercise = (idx: 0 | 1 | 2, field: keyof ExerciseF1Data, value: string) => {
    setModuleF((prev) => {
      const next = [...prev.exercises] as [ExerciseF1Data, ExerciseF1Data, ExerciseF1Data];
      next[idx] = { ...next[idx], [field]: value };
      return { ...prev, exercises: next };
    });
  };

  const hasLoadedGRef = useRef(false);
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("dc2ModuleG");
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<ModuleGData>;
        setModuleG((prev) => ({ ...initialG, ...prev, ...parsed }));
      }
    } catch {
      // ignore
    }
    hasLoadedGRef.current = true;
  }, []);

  useEffect(() => {
    if (!hasLoadedGRef.current) return;
    try {
      sessionStorage.setItem("dc2ModuleG", JSON.stringify(moduleG));
    } catch {
      // ignore
    }
  }, [moduleG]);

  const updateG = (field: keyof ModuleGData, value: string) => {
    setModuleG((prev) => ({ ...prev, [field]: value }));
  };

  // Charger les opérateurs H enregistrés (API)
  useEffect(() => {
    fetch(`${API_BASE}/dc2/operateurs`)
      .then((r) => r.json())
      .then((data) => setSavedHOperateurs(Array.isArray(data) ? data : []))
      .catch(() => setSavedHOperateurs([]));
  }, []);

  const hasLoadedHRef = useRef(false);
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("dc2ModuleHRows");
      if (raw) {
        const parsed = JSON.parse(raw) as HOperateurRow[];
        if (Array.isArray(parsed) && parsed.length > 0) {
          setModuleHRows(parsed);
        }
      }
    } catch {
      // ignore
    }
    hasLoadedHRef.current = true;
  }, []);

  useEffect(() => {
    if (!hasLoadedHRef.current) return;
    try {
      sessionStorage.setItem("dc2ModuleHRows", JSON.stringify(moduleHRows));
    } catch {
      // ignore
    }
  }, [moduleHRows]);

  const addHRow = () => {
    setModuleHRows((prev) => [...prev, { lotNumero: "", nomMembreGroupement: "", identification: "" }]);
  };
  const removeHRow = (index: number) => {
    if (moduleHRows.length <= 1) return;
    setModuleHRows((prev) => prev.filter((_, i) => i !== index));
  };
  const updateHRow = (index: number, field: keyof HOperateurRow, value: string) => {
    setModuleHRows((prev) =>
      prev.map((r, i) => (i === index ? { ...r, [field]: value } : r))
    );
  };
  const handleSaveHOperateurToDb = async (index: number) => {
    const row = moduleHRows[index];
    if (!row) return;
    try {
      const res = await fetch(`${API_BASE}/dc2/operateurs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lotNumero: row.lotNumero,
          nomMembreGroupement: row.nomMembreGroupement,
          identification: row.identification,
        }),
      });
      if (res.ok) {
        const created = await res.json();
        setSavedHOperateurs((prev) => [...prev, created]);
      }
    } catch {
      // ignore
    }
  };
  const handleAddSavedHOperateur = (o: SavedHOperateur) => {
    setModuleHRows((prev) => [
      ...prev,
      { lotNumero: o.lotNumero, nomMembreGroupement: o.nomMembreGroupement, identification: o.identification },
    ]);
  };
  const handleDeleteHOperateur = async (id: number) => {
    try {
      const res = await fetch(`${API_BASE}/dc2/operateurs/${id}`, { method: "DELETE" });
      if (res.ok) {
        setSavedHOperateurs((prev) => prev.filter((o) => o.id !== id));
      }
    } catch {
      // ignore
    }
  };

  /** Payload entièrement plat : une clé par champ, aucun sous-dictionnaire. */
  const getDc2Payload = (): Record<string, string> => {
    const out: Record<string, string> = {};
    out.identificationAcheteur = identificationAcheteur ?? "";
    out.acheteurId = acheteurId ?? "";
    out.nomCommercialDenomination = moduleC1.nomCommercialDenomination ?? "";
    out.adressesPostaleSiege = moduleC1.adressesPostaleSiege ?? "";
    out.adresseElectronique = moduleC1.adresseElectronique ?? "";
    out.telephoneTelecopie = moduleC1.telephoneTelecopie ?? "";
    out.siretOuIdentification = moduleC1.siretOuIdentification ?? "";
    out.formeJuridique = moduleC1.formeJuridique ?? "";
    out.microPetiteMoyenneEntreprise = moduleC1.microPetiteMoyenneEntreprise ?? "";
    moduleC2.forEach((row, idx) => {
      const n = idx + 1;
      out[`c2_${n}_isChecked`] = box(row.isChecked);
      out[`c2_${n}_adresseInternet`] = row.adresseInternet ?? "";
      out[`c2_${n}_renseignements`] = row.renseignements ?? "";
    });
    out.nomListeOfficielle = moduleC3.nomListeOfficielle ?? "";
    out.referencesInscriptionClassification = moduleC3.referencesInscriptionClassification ?? "";
    out.adresseInternetCertificat = moduleC3.adresseInternetCertificat ?? "";
    out.renseignementsAccesCertificat = moduleC3.renseignementsAccesCertificat ?? "";
    out.declareSurHonneur = box(moduleC3.declareSurHonneur);
    out.e1InscriptionRegistre = moduleE.e1InscriptionRegistre ?? "";
    out.e2AutorisationOrganisation = moduleE.e2AutorisationOrganisation ?? "";
    out.e3AdressesInternet = moduleE.e3AdressesInternet ?? "";
    out.e3RenseignementsAcces = moduleE.e3RenseignementsAcces ?? "";
    out.dateCreationOuDebutActivite = moduleF.dateCreationOuDebutActivite ?? "";
    out.f2AutresInfos = moduleF.f2AutresInfos ?? "";
    out.f3ResponsabiliteDecennale = box(moduleF.f3ResponsabiliteDecennale);
    out.f4AdresseInternet = moduleF.f4AdresseInternet ?? "";
    out.f4RenseignementsAcces = moduleF.f4RenseignementsAcces ?? "";
    moduleF.exercises.forEach((ex, idx) => {
      const n = idx + 1;
      out[`f_ex${n}_du`] = ex.du ?? "";
      out[`f_ex${n}_au`] = ex.au ?? "";
      out[`f_ex${n}_chiffreAffairesGlobal`] = ex.chiffreAffairesGlobal ?? "";
      out[`f_ex${n}_partChiffreAffaires`] = ex.partChiffreAffaires ?? "";
    });
    out.g1Recapitulatif = moduleG.g1Recapitulatif ?? "";
    out.g2AdresseInternet = moduleG.g2AdresseInternet ?? "";
    out.g2RenseignementsAcces = moduleG.g2RenseignementsAcces ?? "";
    moduleHRows.forEach((row, idx) => {
      const n = idx + 1;
      out[`h_${n}_lotNumero`] = row.lotNumero ?? "";
      out[`h_${n}_nomMembreGroupement`] = row.nomMembreGroupement ?? "";
      out[`h_${n}_identification`] = row.identification ?? "";
    });
    out.i1Contenu = moduleI.i1Contenu ?? "";
    out.i2AdresseInternet = moduleI.i2AdresseInternet ?? "";
    out.i2RenseignementsAcces = moduleI.i2RenseignementsAcces ?? "";
    return out;
  };

  const handleCreateDc2 = async () => {
    const payload = getDc2Payload();
    setCreating(true);
    setCreateDone(false);
    setCreateError(null);
    try {
      const res = await fetch(`${API_BASE}/dc2`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setCreateDone(true);
      } else {
        setCreateError(typeof data?.detail === "string" ? data.detail : "Erreur lors de la création du DC2");
      }
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : "Erreur réseau ou serveur");
    } finally {
      setCreating(false);
    }
  };

  const handleDownloadDc2 = async () => {
    try {
      const res = await fetch(`${API_BASE}/dc2/download`);
      if (!res.ok) {
        alert("Document non trouvé. Créez-le d'abord via « Créer DC2 ».");
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "dc2.docx";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("Impossible de télécharger le document.");
    }
  };

  const hasLoadedIRef = useRef(false);
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("dc2ModuleI");
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<ModuleIData>;
        setModuleI((prev) => ({ ...initialI, ...prev, ...parsed }));
      }
    } catch {
      // ignore
    }
    hasLoadedIRef.current = true;
  }, []);

  useEffect(() => {
    if (!hasLoadedIRef.current) return;
    try {
      sessionStorage.setItem("dc2ModuleI", JSON.stringify(moduleI));
    } catch {
      // ignore
    }
  }, [moduleI]);

  const updateI = (field: keyof ModuleIData, value: string) => {
    setModuleI((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <section className="dc2-page">
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
            <h1>DC2 — Formulaire</h1>
          </div>
          <p className="dc2-intro">
            Remplissez le formulaire DC2. Les modules sont préremplis depuis les données extraites du PDF.
          </p>

          {/* Module A - Identification de l'acheteur */}
          <div className="dc1-module">
            <h2 className="dc1-module-title">A - Identification de l&apos;acheteur</h2>
            <div className="dc1-module-content">
              <label>
                <span className="dc1-label">Identification de l&apos;acheteur (prérempli par acheteurId)</span>
                <textarea
                  value={identificationAcheteur}
                  onChange={(e) => setIdentificationAcheteur(e.target.value)}
                  rows={4}
                  placeholder="Données issues du PDF (operationType)…"
                />
              </label>
            </div>
          </div>

          {/* Module B - Acheteur (operationType) */}
          <div className="dc1-module">
            <h2 className="dc1-module-title">B - Objet de la consultation</h2>
            <div className="dc1-module-content">
              <label>
                <span className="dc1-label">Acheteur / Mandataire (prérempli par operationType)</span>
                <textarea
                  value={acheteurId}
                  onChange={(e) => setAcheteurId(e.target.value)}
                  rows={4}
                  placeholder="Données issues du PDF (operationType)…"
                />
              </label>
            </div>
          </div>

          {/* Module C - Identification du candidat / membre du groupement */}
          <div className="dc1-module">
            <h2 className="dc1-module-title">
              C - Identification du candidat individuel ou du membre du groupement
            </h2>
            <div className="dc1-module-content">
              {/* Sous-module C1 - Cas général */}
              <div className="dc1-f-section">
                <h3 className="dc1-f-subtitle">C1 - Cas général</h3>
                <p className="dc1-module-instruction dc1-f-text">
                  Nom commercial et dénomination sociale de l&apos;unité ou de l&apos;établissement qui
                  exécutera la prestation, adresses postale et du siège social (si elle est différente
                  de l&apos;adresse postale), adresse électronique, numéros de téléphone et de télécopie,
                  numéro SIRET, à défaut, un numéro d&apos;identification européen ou international ou
                  propre au pays d&apos;origine du candidat issu d&apos;un répertoire figurant dans la
                  liste des ICD :
                </p>
                <div className="dc1-candidate-fields">
                  <label>
                    <span className="dc1-label">Nom commercial et dénomination sociale de l&apos;unité ou de l&apos;établissement qui exécutera la prestation :</span>
                    <input
                      type="text"
                      value={moduleC1.nomCommercialDenomination}
                      onChange={(e) => updateC1("nomCommercialDenomination", e.target.value)}
                    />
                  </label>
                  <label>
                    <span className="dc1-label">Adresses postale et du siège social (si elle est différente de l&apos;adresse postale) :</span>
                    <input
                      type="text"
                      value={moduleC1.adressesPostaleSiege}
                      onChange={(e) => updateC1("adressesPostaleSiege", e.target.value)}
                    />
                  </label>
                  <label>
                    <span className="dc1-label">Adresse électronique :</span>
                    <input
                      type="email"
                      value={moduleC1.adresseElectronique}
                      onChange={(e) => updateC1("adresseElectronique", e.target.value)}
                    />
                  </label>
                  <label>
                    <span className="dc1-label">Numéros de téléphone et de télécopie :</span>
                    <input
                      type="text"
                      value={moduleC1.telephoneTelecopie}
                      onChange={(e) => updateC1("telephoneTelecopie", e.target.value)}
                    />
                  </label>
                  <label>
                    <span className="dc1-label">Numéro SIRET, à défaut numéro d&apos;identification européen ou international ou propre au pays d&apos;origine (liste des ICD) :</span>
                    <input
                      type="text"
                      value={moduleC1.siretOuIdentification}
                      onChange={(e) => updateC1("siretOuIdentification", e.target.value)}
                    />
                  </label>
                </div>
                <p className="dc1-module-instruction dc1-f-text">
                  Forme juridique du candidat individuel ou du membre du groupement (entreprise
                  individuelle, SA, SARL, EURL, association, établissement public, etc.) :
                </p>
                <div className="dc1-lots-fields">
                  <label>
                    <span className="dc1-label">Forme juridique :</span>
                    <input
                      type="text"
                      value={moduleC1.formeJuridique}
                      onChange={(e) => updateC1("formeJuridique", e.target.value)}
                      placeholder="Ex. SA, SARL, EURL, association…"
                    />
                  </label>
                </div>
                <p className="dc1-module-instruction dc1-f-text">
                  Le candidat est-il une micro, une petite ou une moyenne entreprise (entreprises qui
                  occupent moins de 250 personnes et dont le chiffre d&apos;affaires annuel n&apos;excède
                  pas 50 millions d&apos;euros ou dont le total du bilan annuel n&apos;excède pas 43 millions
                  d&apos;euros), au sens de la recommandation de la Commission du 6 mai 2003 concernant
                  la définition des micro, petites et moyennes entreprises (Art. R. 2151-13 et R. 2351-12
                  du code de la commande publique) ?
                </p>
                <div className="dc1-checkbox-list">
                  <label className="dc1-checkbox-row">
                    <span className="dc1-checkbox">{moduleC1.microPetiteMoyenneEntreprise === "oui" ? "☑" : "☐"}</span>
                    <input
                      type="radio"
                      name="dc2-micro-pme"
                      checked={moduleC1.microPetiteMoyenneEntreprise === "oui"}
                      onChange={() => updateC1("microPetiteMoyenneEntreprise", "oui")}
                      className="dc1-checkbox-input"
                    />
                    <span className="dc1-checkbox-text">Oui</span>
                  </label>
                  <label className="dc1-checkbox-row">
                    <span className="dc1-checkbox">{moduleC1.microPetiteMoyenneEntreprise === "non" ? "☑" : "☐"}</span>
                    <input
                      type="radio"
                      name="dc2-micro-pme"
                      checked={moduleC1.microPetiteMoyenneEntreprise === "non"}
                      onChange={() => updateC1("microPetiteMoyenneEntreprise", "non")}
                      className="dc1-checkbox-input"
                    />
                    <span className="dc1-checkbox-text">Non</span>
                  </label>
                </div>
              </div>

              {/* Sous-module C2 - Marchés réservés (tableau) */}
              <div className="dc1-f-section dc2-c2-section">
                <h3 className="dc1-f-subtitle">C2 - Types de marché réservé</h3>
                <p className="dc1-module-instruction dc1-f-text">
                  Indiquer le cas échéant l&apos;adresse internet à laquelle la preuve est accessible directement et gratuitement, ainsi que l&apos;ensemble des renseignements nécessaires pour y accéder.
                </p>
                <div className="dc2-c2-table-wrap">
                  <table className="dc2-c2-table">
                    <thead>
                      <tr>
                        <th className="dc2-c2-th-marche">Type de marché réservé</th>
                        <th className="dc2-c2-th-structure">Type de structure</th>
                        <th className="dc2-c2-th-verif">Éléments permettant la vérification des conditions propres à chaque marché réservé</th>
                      </tr>
                    </thead>
                    <tbody>
                      {C2_STRUCTURE.map((row, idx) => {
                        const data = moduleC2[idx];
                        const rowspan = row.typeMarche
                          ? (() => {
                              let count = 0;
                              for (let i = idx; i < C2_STRUCTURE.length && (i === idx || !C2_STRUCTURE[i].typeMarche); i++) count++;
                              return count;
                            })()
                          : 0;
                        return (
                          <tr key={idx} className="dc2-c2-tr">
                            {row.typeMarche ? (
                              <td className="dc2-c2-td-marche" rowSpan={rowspan}>
                                {row.typeMarche}
                              </td>
                            ) : null}
                            <td className="dc2-c2-td-structure">
                              <label className="dc1-checkbox-row dc2-c2-check">
                                <span className="dc1-checkbox">{data.isChecked ? "☑" : "☐"}</span>
                                <input
                                  type="checkbox"
                                  checked={data.isChecked}
                                  onChange={(e) => updateC2(idx, "isChecked", e.target.checked)}
                                  className="dc1-checkbox-input"
                                />
                                <span className="dc1-checkbox-text dc2-c2-label">{row.typeStructure}</span>
                              </label>
                            </td>
                            <td className="dc2-c2-td-verif">
                              {data.isChecked && (
                                <>
                                  <p className="dc2-c2-instruction">
                                    Le cas échéant, indiquer l&apos;adresse internet à laquelle la preuve est accessible directement et gratuitement, ainsi que l&apos;ensemble des renseignements nécessaires pour y accéder :
                                  </p>
                                  <label className="dc2-c2-field">
                                    <span className="dc1-label">Adresse internet :</span>
                                    <input
                                      type="url"
                                      value={data.adresseInternet}
                                      onChange={(e) => updateC2(idx, "adresseInternet", e.target.value)}
                                      placeholder="https://…"
                                    />
                                  </label>
                                  <label className="dc2-c2-field">
                                    <span className="dc1-label">Renseignements nécessaires pour y accéder :</span>
                                    <input
                                      type="text"
                                      value={data.renseignements}
                                      onChange={(e) => updateC2(idx, "renseignements", e.target.value)}
                                    />
                                  </label>
                                </>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Sous-module C3 - Cas spécifiques relatifs aux conditions de participation */}
              <div className="dc1-f-section dc2-c3-section">
                <h3 className="dc1-f-subtitle">C3 - Cas spécifiques relatifs aux conditions de participation</h3>

                <p className="dc1-module-instruction dc1-f-text dc2-c3-intro">
                  1. Lorsque le candidat est inscrit sur une liste officielle d&apos;opérateurs économiques agréés au sens de l&apos;article R. 2143-15 du code de la commande publique et que l&apos;acheteur est un pouvoir adjudicateur ou au sens des articles R. 2343-16 à R. 2343-17 du même code, que l&apos;acheteur soit un pouvoir adjudicateur ou une entité adjudicatrice :
                </p>
                <div className="dc1-candidate-fields">
                  <label>
                    <span className="dc1-label">Indication du nom de la liste officielle :</span>
                    <input
                      type="text"
                      value={moduleC3.nomListeOfficielle}
                      onChange={(e) => updateC3("nomListeOfficielle", e.target.value)}
                    />
                  </label>
                  <label>
                    <span className="dc1-label">Références sur lesquelles l&apos;inscription ou la certification est basée et, le cas échéant, la classification sur la liste :</span>
                    <textarea
                      value={moduleC3.referencesInscriptionClassification}
                      onChange={(e) => updateC3("referencesInscriptionClassification", e.target.value)}
                      rows={3}
                    />
                  </label>
                  <p className="dc2-c3-note">
                    (L&apos;attention du candidat est attirée sur le fait qu&apos;il convient de remplir les rubriques suivantes du présent formulaire pour l&apos;ensemble des conditions de participation fixées par l&apos;acheteur et qui ne seraient pas couvertes par les conditions d&apos;inscription sur la liste officielle ou le certificat d&apos;inscription sur cette liste)
                  </p>
                  <p className="dc1-module-instruction dc1-f-text">
                    Le cas échéant, adresse internet à laquelle le certificat d&apos;inscription sur cette liste officielle est accessible directement et gratuitement, ainsi que l&apos;ensemble des renseignements nécessaires pour y accéder :
                  </p>
                  <label>
                    <span className="dc1-label">Adresse internet :</span>
                    <input
                      type="url"
                      value={moduleC3.adresseInternetCertificat}
                      onChange={(e) => updateC3("adresseInternetCertificat", e.target.value)}
                      placeholder="https://…"
                    />
                  </label>
                  <label>
                    <span className="dc1-label">Renseignements nécessaires pour y accéder :</span>
                    <input
                      type="text"
                      value={moduleC3.renseignementsAccesCertificat}
                      onChange={(e) => updateC3("renseignementsAccesCertificat", e.target.value)}
                    />
                  </label>
                </div>

                <p className="dc1-module-instruction dc1-f-text dc2-c3-intro">
                  2. Lorsque le marché public n&apos;est pas un marché de défense ou de sécurité et que l&apos;acheteur a autorisé les candidats à se limiter à indiquer qu&apos;ils disposent de l&apos;aptitude et des capacités requises en application du second alinéa de l&apos;article R. 2143-4 du code de la commande publique :
                </p>
                <div className="dc1-checkbox-list">
                  <label className="dc1-checkbox-row">
                    <span className="dc1-checkbox">{moduleC3.declareSurHonneur ? "☑" : "☐"}</span>
                    <input
                      type="checkbox"
                      checked={moduleC3.declareSurHonneur}
                      onChange={(e) => updateC3("declareSurHonneur", e.target.checked)}
                      className="dc1-checkbox-input"
                    />
                    <span className="dc1-checkbox-text">
                      Le candidat déclare sur l&apos;honneur satisfaire à l&apos;ensemble des conditions de participation requises par l&apos;acheteur.
                    </span>
                  </label>
                </div>
                <p className="dc2-c3-note">
                  (Dans ce cas, il est inutile de remplir les rubriques suivantes du présent formulaire ; le remplissage du formulaire est terminé)
                </p>
              </div>
            </div>
          </div>

          {/* Module E - Aptitude à exercer l'activité professionnelle */}
          <div className="dc1-module">
            <h2 className="dc1-module-title">
              E - Renseignements relatifs à l&apos;aptitude à exercer l&apos;activité professionnelle concernée par le contrat
            </h2>
            <div className="dc1-module-content">
              <p className="dc2-module-e-intro">
                <em>Le candidat ne fournit que les renseignements demandés par l&apos;acheteur au titre de l&apos;aptitude à exercer l&apos;activité professionnelle.</em>
              </p>
              <p className="dc2-module-e-note">
                (En cas de MDS, les documents de preuve sont à fournir avec la candidature, sauf cas particulier de la rubrique E3)
              </p>

              <div className="dc1-f-section dc2-module-e-section">
                <label>
                  <span className="dc1-label dc2-e-subtitle">E1 - Renseignements sur l&apos;inscription sur un registre professionnel :</span>
                  <textarea
                    value={moduleE.e1InscriptionRegistre}
                    onChange={(e) => updateE("e1InscriptionRegistre", e.target.value)}
                    rows={3}
                  />
                </label>
              </div>

              <div className="dc1-f-section dc2-module-e-section">
                <label>
                  <span className="dc1-label dc2-e-subtitle">
                    E2 - Le cas échéant, pour les marchés publics de services, indication de l&apos;autorisation spécifique dont le candidat doit être doté ou de l&apos;organisation spécifique dont il doit être membre pour pouvoir fournir, dans son pays d&apos;origine, le service concerné :
                  </span>
                  <textarea
                    value={moduleE.e2AutorisationOrganisation}
                    onChange={(e) => updateE("e2AutorisationOrganisation", e.target.value)}
                    rows={3}
                  />
                </label>
              </div>

              <div className="dc1-f-section dc2-module-e-section">
                <p className="dc1-label dc2-e-subtitle dc2-e3-title">
                  E3 - Le cas échéant, adresse internet à laquelle les documents justificatifs et moyens de preuve sont accessibles directement et gratuitement, ainsi que l&apos;ensemble des renseignements nécessaires pour y accéder (applicable pour tous les marchés publics autres que MDS et, pour les MDS, uniquement lorsque l&apos;acheteur a autorisé les candidats à ne pas fournir ces documents de preuve en application de l&apos;article <span className="dc2-e-ref">R. 2343-14</span> du code de la commande publique) :
                </p>
                <p className="dc2-module-e-note">
                  (Si l&apos;adresse et les renseignements sont identiques à ceux fournis plus haut se contenter de renvoyer à la rubrique concernée)
                </p>
                <label className="dc2-e3-field">
                  <span className="dc1-label">Adresse(s) internet :</span>
                  <input
                    type="url"
                    value={moduleE.e3AdressesInternet}
                    onChange={(e) => updateE("e3AdressesInternet", e.target.value)}
                    placeholder="https://…"
                  />
                </label>
                <label className="dc2-e3-field">
                  <span className="dc1-label">Renseignements nécessaires pour y accéder :</span>
                  <input
                    type="text"
                    value={moduleE.e3RenseignementsAcces}
                    onChange={(e) => updateE("e3RenseignementsAcces", e.target.value)}
                  />
                </label>
              </div>
            </div>
          </div>

          {/* Module F - Capacité économique et financière */}
          <div className="dc1-module">
            <h2 className="dc1-module-title">
              F - Renseignements relatifs à la capacité économique et financière du candidat individuel ou du membre du groupement
            </h2>
            <div className="dc1-module-content">
              <p className="dc2-module-e-intro">
                <em>Le candidat ne fournit que les renseignements demandés par l&apos;acheteur au titre de la capacité économique et financière.</em>
              </p>
              <p className="dc2-module-e-note">
                (En cas de MDS, les documents de preuve sont à fournir avec la candidature, sauf cas particulier de la rubrique F4)
              </p>

              {/* Sous-module F1 - Chiffres d'affaires */}
              <div className="dc1-f-section dc2-module-f1-section">
                <h3 className="dc1-f-subtitle">F1 - Chiffres d&apos;affaires hors taxes des trois derniers exercices disponibles</h3>
                <div className="dc2-f1-table-wrap">
                  <table className="dc2-f1-table">
                    <thead>
                      <tr>
                        <th className="dc2-f1-th-label"></th>
                        {([0, 1, 2] as const).map((i) => (
                          <th key={i} className="dc2-f1-th-ex">
                            <span className="dc2-f1-ex-label">Exercice du</span>
                            <input
                              type="text"
                              value={moduleF.exercises[i].du}
                              onChange={(e) => updateFExercise(i, "du", e.target.value)}
                              placeholder="jj/mm/aaaa"
                              className="dc2-f1-date-input"
                            />
                            <span className="dc2-f1-ex-label">au</span>
                            <input
                              type="text"
                              value={moduleF.exercises[i].au}
                              onChange={(e) => updateFExercise(i, "au", e.target.value)}
                              placeholder="jj/mm/aaaa"
                              className="dc2-f1-date-input"
                            />
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td className="dc2-f1-td-label">
                          Chiffre d&apos;affaires global (ne remplir que pour les exercices pour lesquels ce renseignement est demandé par l&apos;acheteur)
                        </td>
                        {([0, 1, 2] as const).map((i) => (
                          <td key={i} className="dc2-f1-td-input">
                            <input
                              type="text"
                              inputMode="decimal"
                              value={moduleF.exercises[i].chiffreAffairesGlobal}
                              onChange={(e) => updateFExercise(i, "chiffreAffairesGlobal", e.target.value)}
                            />
                          </td>
                        ))}
                      </tr>
                      <tr>
                        <td className="dc2-f1-td-label">
                          Part du chiffre d&apos;affaires concernant les fournitures, services, ou travaux objet
                          <div className="dc2-f1-td-sublabel">du marché (si demandé par l&apos;acheteur)</div>
                        </td>
                        {([0, 1, 2] as const).map((i) => (
                          <td key={i} className="dc2-f1-td-input dc2-f1-td-pct">
                            <input
                              type="text"
                              inputMode="decimal"
                              value={moduleF.exercises[i].partChiffreAffaires}
                              onChange={(e) => updateFExercise(i, "partChiffreAffaires", e.target.value)}
                              placeholder="%"
                            />
                            <span className="dc2-f1-pct">%</span>
                          </td>
                        ))}
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="dc2-f1-instruction">
                  Lorsque les informations sur le chiffre d&apos;affaires ne sont pas disponibles pour la totalité de la période demandée, indication de la date à laquelle l&apos;opérateur économique a été créé ou a commencé son activité :
                </p>
                <label className="dc2-f1-date-field">
                  <input
                    type="text"
                    value={moduleF.dateCreationOuDebutActivite}
                    onChange={(e) => setModuleF((prev) => ({ ...prev, dateCreationOuDebutActivite: e.target.value }))}
                    placeholder="jj/mm/aaaa"
                  />
                </label>
              </div>

              {/* Sous-module F2 */}
              <div className="dc1-f-section dc2-module-f-section">
                <h3 className="dc1-f-subtitle">F2 - Autres informations requises par l&apos;acheteur au titre de la capacité économique et financière</h3>
                <p className="dc2-f2-desc">
                  Chiffres d&apos;affaires moyens sur la période demandée par l&apos;acheteur, informations sur les comptes annuels, rapport entre les éléments d&apos;actif et de passif, informations sur le niveau approprié d&apos;assurance des risques professionnels, etc., tels que demandés par l&apos;acheteur. Le cas échéant, renvoyer à la rubrique H du présent formulaire.
                </p>
                <label>
                  <textarea
                    value={moduleF.f2AutresInfos}
                    onChange={(e) => setModuleF((prev) => ({ ...prev, f2AutresInfos: e.target.value }))}
                    rows={4}
                    placeholder="Indiquez les informations demandées ou renvoyez à la rubrique H…"
                  />
                </label>
              </div>

              {/* Sous-module F3 */}
              <div className="dc1-f-section dc2-module-f-section">
                <h3 className="dc1-f-subtitle">F3 - Pour les marchés publics de travaux</h3>
                <label className="dc1-checkbox-row dc2-f3-check">
                  <span className="dc1-checkbox">{moduleF.f3ResponsabiliteDecennale ? "☑" : "☐"}</span>
                  <input
                    type="checkbox"
                    checked={moduleF.f3ResponsabiliteDecennale}
                    onChange={(e) => setModuleF((prev) => ({ ...prev, f3ResponsabiliteDecennale: e.target.checked }))}
                    className="dc1-checkbox-input"
                  />
                  <span className="dc1-checkbox-text">
                    En cochant cette case, le candidat déclare qu&apos;il aura souscrit un contrat d&apos;assurance le couvrant au regard de la responsabilité décennale (<span className="dc2-e-ref">article L. 241-1</span> du code des assurances).
                  </span>
                </label>
                <p className="dc2-module-e-note dc2-f3-note">
                  (Y compris en cas de <span className="dc2-e-ref">MDS</span>, les documents de preuve ne seront sollicités sur ce point qu&apos;avant l&apos;attribution du marché public)
                </p>
              </div>

              {/* Sous-module F4 */}
              <div className="dc1-f-section dc2-module-f-section">
                <h3 className="dc1-f-subtitle">
                  F4 - Documents de preuve disponibles en ligne
                </h3>
                <p className="dc2-f4-applicable">
                  (applicable pour tous les marchés publics autres que MDS et, pour les MDS, uniquement lorsque l&apos;acheteur a autorisé les candidats à ne pas fournir ces documents de preuve en application de l&apos;article <span className="dc2-e-ref">R. 2343-14</span> du code de la commande publique)
                </p>
                <p className="dc2-f4-request">
                  Le cas échéant, adresse internet à laquelle les documents justificatifs et moyens de preuve sont accessibles directement et gratuitement, ainsi que l&apos;ensemble des renseignements nécessaires pour y accéder :
                </p>
                <p className="dc2-module-e-note">
                  (Si l&apos;adresse et les renseignements sont identiques à ceux fournis plus haut se contenter de renvoyer à la rubrique concernée)
                </p>
                <label className="dc2-e3-field">
                  <span className="dc1-label">Adresse internet :</span>
                  <input
                    type="url"
                    value={moduleF.f4AdresseInternet}
                    onChange={(e) => setModuleF((prev) => ({ ...prev, f4AdresseInternet: e.target.value }))}
                    placeholder="https://…"
                  />
                </label>
                <label className="dc2-e3-field">
                  <span className="dc1-label">Renseignements nécessaires pour y accéder :</span>
                  <input
                    type="text"
                    value={moduleF.f4RenseignementsAcces}
                    onChange={(e) => setModuleF((prev) => ({ ...prev, f4RenseignementsAcces: e.target.value }))}
                  />
                </label>
              </div>
            </div>
          </div>

          {/* Module G - Capacité technique et professionnelle */}
          <div className="dc1-module">
            <h2 className="dc1-module-title">
              G - Renseignements relatifs à la capacité technique et professionnelle du candidat individuel ou du membre du groupement
            </h2>
            <div className="dc1-module-content">
              <p className="dc2-module-e-intro">
                <em>Le candidat ne fournit que les renseignements demandés par l&apos;acheteur au titre de la capacité technique et professionnelle.</em>
              </p>
              <p className="dc2-module-e-note">
                (En cas de MDS, les documents de preuve sont à fournir avec la candidature, sauf cas particulier de la rubrique G2)
              </p>

              {/* Sous-module G1 */}
              <div className="dc1-f-section dc2-module-g-section">
                <h3 className="dc1-f-subtitle">
                  G1 - Le candidat ne fournit que les renseignements demandés par l&apos;acheteur au titre de la capacité technique et professionnelle, qu&apos;il peut récapituler ici
                </h3>
                <label>
                  <textarea
                    value={moduleG.g1Recapitulatif}
                    onChange={(e) => updateG("g1Recapitulatif", e.target.value)}
                    rows={4}
                    placeholder="Récapitulatif des renseignements demandés…"
                  />
                </label>
              </div>

              {/* Sous-module G2 */}
              <div className="dc1-f-section dc2-module-g-section">
                <h3 className="dc1-f-subtitle dc2-g2-title">
                  G2 - Documents de preuve disponibles en ligne (applicable pour tous les marchés publics autres que MDS et, pour les MDS, uniquement lorsque l&apos;acheteur a autorisé les candidats à ne pas fournir ces documents de preuve en application de l&apos;article <span className="dc2-e-ref">R. 2343-14</span> du code de la commande publique) :
                </h3>
                <p className="dc2-f4-request">
                  Le cas échéant, adresse internet à laquelle les documents justificatifs et moyens de preuve sont accessibles directement et gratuitement, ainsi que l&apos;ensemble des renseignements nécessaires pour y accéder :
                </p>
                <p className="dc2-module-e-note">
                  (Si l&apos;adresse et les renseignements sont identiques à ceux fournis plus haut se contenter de renvoyer à la rubrique concernée)
                </p>
                <label className="dc2-e3-field">
                  <span className="dc1-label">Adresse internet :</span>
                  <input
                    type="url"
                    value={moduleG.g2AdresseInternet}
                    onChange={(e) => updateG("g2AdresseInternet", e.target.value)}
                    placeholder="https://…"
                  />
                </label>
                <label className="dc2-e3-field">
                  <span className="dc1-label">Renseignements nécessaires pour y accéder :</span>
                  <input
                    type="text"
                    value={moduleG.g2RenseignementsAcces}
                    onChange={(e) => updateG("g2RenseignementsAcces", e.target.value)}
                  />
                </label>
              </div>
            </div>
          </div>

          {/* Module H - Capacités des opérateurs économiques */}
          <div className="dc1-module dc1-module-groupement">
            <h2 className="dc1-module-title">
              H - Capacités des opérateurs économiques sur lesquels le candidat individuel ou le membre du groupement s&apos;appuie pour présenter sa candidature
            </h2>
            <p className="dc1-module-instruction dc2-module-h-intro">
              Lorsque le candidat individuel ou le membre du groupement s&apos;appuie sur les capacités d&apos;autres opérateurs économiques, quelle que soit la nature juridique des liens qui les unissent (sous-traitant, co-traitant, etc.), conformément aux articles R. 2142-3 et R. 2342-2 du code de la commande publique. Les renseignements relatifs aux co-traitants figurent en priorité aux rubriques F ou G.
            </p>
            <p className="dc1-module-instruction dc2-module-h-intro">
              Joindre un DC2 ou équivalent pour chaque opérateur économique, comportant l&apos;ensemble des renseignements demandés dans l&apos;avis d&apos;appel public à la concurrence. Lorsque l&apos;opérateur économique sur les capacités duquel le candidat s&apos;appuie est un sous-traitant, les renseignements sont fournis via DC4 ou équivalent. Dans les autres cas, une annexe DC2 ou équivalent peut être utilisée. Le candidat justifie que chaque opérateur mettra les moyens nécessaires à disposition pendant l&apos;exécution du marché. En cas de MDS, cette justification est fournie au moment du dépôt de la candidature.
            </p>
            <div className="dc1-groupement-load">
              <label>
                <span className="dc1-label">
                  {savedHOperateurs.length > 0
                    ? "Ajouter un opérateur enregistré :"
                    : "Aucun opérateur enregistré pour le moment."}
                </span>
                {savedHOperateurs.length > 0 && (
                  <select
                    className="dc1-select-groupement"
                    value=""
                    onChange={(e) => {
                      const id = e.target.value ? parseInt(e.target.value, 10) : 0;
                      if (id) {
                        const o = savedHOperateurs.find((x) => x.id === id);
                        if (o) handleAddSavedHOperateur(o);
                      }
                      e.target.value = "";
                    }}
                  >
                    <option value="">— Sélectionner —</option>
                    {savedHOperateurs.map((o) => {
                      const label = o.identification
                        ? (o.identification.length > 35 ? o.identification.slice(0, 35) + "…" : o.identification)
                        : "(vide)";
                      return (
                        <option key={o.id} value={o.id}>
                          Lot {o.lotNumero || "—"} · {o.nomMembreGroupement || "—"} · {label} · {new Date(o.created_at || "").toLocaleDateString("fr-FR")}
                        </option>
                      );
                    })}
                  </select>
                )}
              </label>
              {savedHOperateurs.length > 0 && (
                <ul className="dc1-saved-members-list">
                  {savedHOperateurs.map((o) => (
                    <li key={o.id} className="dc1-saved-member-item">
                      <span className="dc1-saved-member-label">
                        Lot {o.lotNumero || "—"} · {o.nomMembreGroupement || "—"} · {(o.identification || "(vide)").slice(0, 40)}
                        {(o.identification?.length ?? 0) > 40 ? "…" : ""}
                      </span>
                      <button
                        type="button"
                        className="dc1-btn-delete-member"
                        onClick={() => handleDeleteHOperateur(o.id)}
                        title="Supprimer cet opérateur de la base"
                      >
                        Supprimer
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="dc1-module-content">
              <h3 className="dc1-f-subtitle dc2-h-table-title">Désignation du (des) opérateur(s) (Adapter le tableau autant que nécessaire)</h3>
              <div className="dc1-table-wrap">
                <table className="dc1-table dc2-h-table">
                  <thead>
                    <tr>
                      <th className="dc2-h-th-lot">N° du Lot</th>
                      <th className="dc2-h-th-nom">Nom du membre du groupement concerné</th>
                      <th className="dc2-h-th-id">
                        Nom commercial et dénomination sociale, adresse de l&apos;établissement, adresse électronique, numéros de téléphone et de télécopie, numéro SIRET de l&apos;opérateur sur les capacités duquel le candidat ou le membre du groupement s&apos;appuie
                      </th>
                      <th className="dc1-th-actions">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {moduleHRows.map((row, index) => (
                      <tr key={index}>
                        <td>
                          <input
                            type="text"
                            value={row.lotNumero}
                            onChange={(e) => updateHRow(index, "lotNumero", e.target.value)}
                            placeholder="ex. 1"
                          />
                        </td>
                        <td>
                          <input
                            type="text"
                            value={row.nomMembreGroupement}
                            onChange={(e) => updateHRow(index, "nomMembreGroupement", e.target.value)}
                            placeholder="Nom du membre"
                          />
                        </td>
                        <td>
                          <textarea
                            value={row.identification}
                            onChange={(e) => updateHRow(index, "identification", e.target.value)}
                            rows={2}
                            placeholder="Nom commercial, dénomination sociale, adresse, email, tél, SIRET…"
                          />
                        </td>
                        <td>
                          <div className="dc1-row-actions">
                            <button
                              type="button"
                              className="dc1-btn-save-member"
                              onClick={() => handleSaveHOperateurToDb(index)}
                              title="Enregistrer cet opérateur"
                            >
                              Enregistrer
                            </button>
                            <button
                              type="button"
                              className="dc1-btn-remove"
                              onClick={() => removeHRow(index)}
                              disabled={moduleHRows.length <= 1}
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
                <button type="button" className="dc1-btn-add" onClick={addHRow}>
                  + Ajouter une ligne
                </button>
              </div>
            </div>
          </div>

          {/* Module I - Informations complémentaires et attestations */}
          <div className="dc1-module">
            <h2 className="dc1-module-title">
              I - Informations complémentaires et attestations du candidat
            </h2>
            <div className="dc1-module-content">
              {/* Sous-module I1 */}
              <div className="dc1-f-section dc2-module-i-section">
                <h3 className="dc1-f-subtitle">
                  I1 - Informations complémentaires demandées par l&apos;acheteur
                </h3>
                <label>
                  <textarea
                    value={moduleI.i1Contenu}
                    onChange={(e) => updateI("i1Contenu", e.target.value)}
                    rows={4}
                    placeholder="Indiquez les informations complémentaires demandées par l&apos;acheteur…"
                  />
                </label>
              </div>

              {/* Sous-module I2 */}
              <div className="dc1-f-section dc2-module-i-section">
                <h3 className="dc1-f-subtitle">
                  I2 - Documents de preuve disponibles en ligne
                </h3>
                <p className="dc2-f4-request">
                  Le cas échéant, adresse internet à laquelle les documents justificatifs et moyens de preuve sont accessibles directement et gratuitement, ainsi que l&apos;ensemble des renseignements nécessaires pour y accéder :
                </p>
                <p className="dc2-module-e-note">
                  (Si l&apos;adresse et les renseignements sont identiques à ceux fournis plus haut se contenter de renvoyer à la rubrique concernée)
                </p>
                <label className="dc2-e3-field">
                  <span className="dc1-label">Adresse internet :</span>
                  <input
                    type="url"
                    value={moduleI.i2AdresseInternet}
                    onChange={(e) => updateI("i2AdresseInternet", e.target.value)}
                    placeholder="https://…"
                  />
                </label>
                <label className="dc2-e3-field">
                  <span className="dc1-label">Renseignements nécessaires pour y accéder :</span>
                  <input
                    type="text"
                    value={moduleI.i2RenseignementsAcces}
                    onChange={(e) => updateI("i2RenseignementsAcces", e.target.value)}
                  />
                </label>
              </div>
            </div>
          </div>

          {createError && (
            <div className="dc2-error" role="alert">
              {createError}
              <button type="button" className="dc2-error-dismiss" onClick={() => setCreateError(null)} aria-label="Fermer">×</button>
            </div>
          )}
          <div className="dc2-actions">
            <button
              type="button"
              className="dc2-save"
              onClick={handleCreateDc2}
              disabled={creating}
              title="Envoyer toutes les données DC2 au serveur"
            >
              {creating ? "Envoi…" : createDone ? "✓ DC2 envoyé" : "Créer DC2"}
            </button>
            <button
              type="button"
              className="dc2-download"
              onClick={handleDownloadDc2}
              title="Télécharger le document DC2"
            >
              Télécharger DC2
            </button>
            <Link to="/dc1" className="dc2-back">
              ← Retour au DC1
            </Link>
            <Link to="/results" className="dc2-back">
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

      {/* Bouton Chat PDF */}
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
        <div className="results-chat-overlay results-chat-overlay--side" aria-modal="true" role="dialog" aria-labelledby="dc2-chat-title">
          <div className="results-chat-backdrop" onClick={() => setChatOpen(false)} />
          <div className="results-chat-window results-chat-window--side">
            <div className="results-chat-header">
              <h2 id="dc2-chat-title" className="results-chat-title">Chat PDF</h2>
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
              Question LLM + <strong>keyword</strong> + <strong>rerank</strong> → réponse sur le dernier PDF analysé.
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

export default Dc2;
