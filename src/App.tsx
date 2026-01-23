import { useState } from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Results from "./components/Results";
// import Home from "./components/Home"
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Header from "./components/Header"
import Grabpdf from "./components/Grabpdf"
import Home from "./components/Home"

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <div>
//         <a href="https://vite.dev" target="_blank">
//           <img src={viteLogo} className="logo" alt="Vite logo" />
//         </a>
//         <a href="https://react.dev" target="_blank">
//           <img src={reactLogo} className="logo react" alt="React logo" />
//         </a>
//       </div>
//       <h1>Vite + React</h1>
//       <div className="card">
//         <button onClick={() => setCount((count) => count + 1)}>
//           count is {count}
//         </button>
//         <p>
//           Edit <code>src/App.tsx</code> and save to test HMR
//         </p>
//       </div>
//       <p className="read-the-docs">
//         Click on the Vite and React logos to learn more
//       </p>
//     </>
//   )
// }


// Type pour les questions
type QuestionType = { question: string; reponse: string };

function App() {
  // 1️⃣ State global pour stocker les questions
  const [questions, setQuestions] = useState<QuestionType[]>([]);

  return (
    <BrowserRouter>
      <Routes>
        {/* 2️⃣ Page d’accueil */}
        <Route path="/" element={<Home setQuestions={setQuestions} />} />

        {/* 3️⃣ Page de résultats */}
        <Route path="/results" element={<Results questions={questions} />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App
