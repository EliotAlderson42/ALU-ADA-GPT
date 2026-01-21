import {useState} from "react"

function Home() {
    const [count, setCount] = useState(0)

    return (
    <main>
        <h2>Bienvenue</h2>
        <p>Compteur : {count}</p>
        <button onClick={() => setCount(count + 1)}>
            Cliquer
        </button>
    </main>
    );
}

export default Home