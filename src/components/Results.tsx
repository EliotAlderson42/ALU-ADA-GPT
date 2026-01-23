function Results({ questions }: { questions: QuestionType[] }) {
  return (
    <div>
      <h1>Résultats</h1>

      {questions.length === 0 ? (
        <p>Aucune question à afficher.</p>
      ) : (
        <ul>
          {questions.map((q, index) => (
            <li key={index}>
              <strong>Q:</strong> {q.question} <br />
              <strong>R:</strong> {q.reponse}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Results;