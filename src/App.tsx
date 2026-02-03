import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import Header from "./components/Header";
import Home from "./components/Home";
import Results from "./components/Results";
import Questions from "./components/Questions";

// Type partagé pour les questions/réponses
export type Question = { question: string; reponse: string };

function App() {
  // State global pour stocker les questions générées par le backend
  const [questions, setQuestions] = useState<Question[]>([]);

  return (
    <BrowserRouter>
      <div className="app-shell">
        <Header />

        <main className="app-main">
          <Routes>
            {/* Page d’accueil : upload du PDF */}
            <Route path="/" element={<Home setQuestions={setQuestions} />} />

            {/* Page de résultats : affiche les QA */}
            <Route path="/results" element={<Results questions={questions} />} />

            {/* Gestion des questions RAG (base de données) */}
            <Route path="/questions" element={<Questions />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <span>ALU / ADA GPT • Projet RAG PDF</span>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;

