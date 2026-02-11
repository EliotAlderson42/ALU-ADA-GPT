import { Link } from "react-router-dom";
import type { Question } from "../App";
import { normalizeNewlines } from "../utils";

type ResultsProps = {
  questions: Question[];
};

function Results({ questions }: ResultsProps) {
  return (
    <section className="results">
      <h1>Résultats</h1>

      <Link to="/dc1" className="results-dc1-btn">
        Start DC1
      </Link>

      {questions.length === 0 ? (
        <p>Aucune question à afficher pour le moment.</p>
      ) : (
        <ul className="results-list">
          {questions.map((q, index) => (
            <li key={index} className="question-card">
              <h2>Question {index + 1}</h2>
              <p className="question-text">{q.question}</p>
              <p className="answer-text">{normalizeNewlines(q.reponse)}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default Results;