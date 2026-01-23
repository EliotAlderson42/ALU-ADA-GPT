// import {useState} from "react"
import { useNavigate } from "react-router-dom"
import PdfUploaderDragDrop from "./Grabpdf";

function Home({ setQuestions }: { setQuestions: any }) {
  const navigate = useNavigate();

  const handlePdfSelected = async (file: File) => {
    // 1️⃣ Préparer le formulaire
    const formData = new FormData();
    formData.append("file", file);

    // 2️⃣ Envoyer au backend
    const res = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData,
    });

    // 3️⃣ Recevoir les questions
    const data = await res.json();
    const tab = Object.entries(data).map(([question, reponse]) => ({
      question,
      reponse,
    }));

    // 4️⃣ Stocker dans le state global
    setQuestions(tab);

    // 5️⃣ Naviguer vers la page résultats
    navigate("/results");
  };

  return (
    <div>
      <PdfUploaderDragDrop onFileSelected={handlePdfSelected} />
    </div>
  );
}

export default Home;