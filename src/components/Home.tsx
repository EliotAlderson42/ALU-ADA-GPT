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
    // Réinitialiser les erreurs précédentes
    setError(null);
    setIsProcessing(true);
    setUploadedFileName(file.name);

    // 1️⃣ Préparer le formulaire
    const formData = new FormData();
    formData.append("file", file, file.name);

    try {
      // 2️⃣ Envoyer au backend
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: `Erreur serveur (${res.status})` }));
        throw new Error(errorData.detail || `Erreur serveur (${res.status})`);
      }

      // 3️⃣ Recevoir les questions : ton backend renvoie déjà un tableau
      const data: Question[] = await res.json();

      // 4️⃣ Stocker dans le state global
      setQuestions(data);

      // 5️⃣ Naviguer vers la page résultats
      navigate("/results");
    } catch (e) {
      console.error(e);
      const errorMessage = e instanceof Error ? e.message : "Une erreur est survenue lors de l'analyse du PDF.";
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