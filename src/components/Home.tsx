import { useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { useNavigate } from "react-router-dom";
import PdfUploaderDragDrop from "./Grabpdf";
import type { Question } from "../App";

type HomeProps = {
  setQuestions: Dispatch<SetStateAction<Question[]>>;
};

function Home({ setQuestions }: HomeProps) {
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePdfSelected = async (file: File) => {
    setError(null);
    setIsProcessing(true);
    setUploadedFileName(file.name);
    console.log("[Front] Fichier sélectionné:", file.name);

    // Vérifier que le backend répond avant d'envoyer le PDF
    // const healthAbort = new AbortController();
    // const healthTimeout = setTimeout(() => healthAbort.abort(), 3000);
    // try {
    //   const healthRes = await fetch("http://127.0.0.1:8001/health", { signal: healthAbort.signal });
    //   clearTimeout(healthTimeout);
    //   if (!healthRes.ok) throw new Error("Backend ne répond pas correctement");
    //   console.log("[Front] Backend joignable, envoi du PDF...");
    // } catch (healthErr) {
    //   clearTimeout(healthTimeout);
    //   console.error("[Front] Backend injoignable:", healthErr);
    //   setError("Backend injoignable (port 8010). Lancez depuis la racine : uvicorn backend.main:app --reload --port 8010");
    //   setIsProcessing(false);
    //   return;
    // }

    const formData = new FormData();
    formData.append("file", file, file.name);

    const controller = new AbortController();
    // const timeoutId = setTimeout(() => controller.abort(), 120_000);

    try {
      const res = await fetch("http://127.0.0.1:8011/upload", {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });

      // clearTimeout(timeoutId);

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: `Erreur serveur (${res.status})` }));
        throw new Error(errorData.detail || `Erreur serveur (${res.status})`);
      }

      // 3️⃣ Recevoir questions (affichage) et data (sauvegarde)
      const { questions: qr, data } = (await res.json()) as {
        questions: Question[];
        data: unknown;
      };

      // 4️⃣ Afficher q_r sur la page résultats
      setQuestions(qr);

      // 5️⃣ Sauvegarder data pour une future page (Word, export, etc.)
      sessionStorage.setItem("ragData", JSON.stringify(data));

      // 6️⃣ Naviguer vers la page résultats
      navigate("/results");
    } catch (e) {
      // clearTimeout(timeoutId);
      console.error(e);
      let errorMessage: string;
      if (e instanceof Error) {
        if (e.name === "AbortError") {
          errorMessage =
            "Délai dépassé (2 min). Vérifiez que le backend et Ollama tournent, et que le PDF n'est pas trop lourd.";
        } else {
          errorMessage =
            e.message.includes("Failed to fetch") || e.message.includes("Load failed")
              ? "Le serveur ne répond pas. Lancez le backend depuis la racine du projet : uvicorn backend.main:app --reload --port 8010"
              : e.message;
        }
      } else {
        errorMessage = "Une erreur est survenue lors de l'analyse du PDF.";
      }
      setError(errorMessage);
      setIsProcessing(false);
    }
  };

  return (
    <section className="home">
      <div className="home-intro">
        <h1>ALU / ADA GPT</h1>
        <p>
          Dépose ton pdf
        </p>
      </div>

      {isProcessing ? (
        <div className="processing-container">
          <div className="processing-spinner"></div>
          <h2 className="processing-title">Document pris en charge</h2>
          <p className="processing-filename">{uploadedFileName}</p>
          <p className="processing-message">
            Analyse en cours... Cela peut prendre quelques instants.
          </p>
        </div>
      ) : (
        <>
          <PdfUploaderDragDrop onFileSelected={handlePdfSelected} />
          {error && (
            <div className="error-message">
              <strong>Erreur :</strong> {error}
            </div>
          )}
        </>
      )}
    </section>
  );
}

export default Home;