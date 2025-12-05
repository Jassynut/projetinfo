import { useParams } from "react-router-dom";
import { useState } from "react";

export default function EnterCinPage() {
  const { testId } = useParams();
  const [cin, setCin] = useState("");
  const [message, setMessage] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();

    const response = await fetch(
      `http://localhost:8000/api/mobile/test/${testId}/start/`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cin }),
      }
    );

    const data = await response.json();
    setMessage(JSON.stringify(data, null, 2));
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Entrer votre CIN pour démarrer le test</h1>
      <p>Test ID: {testId}</p>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Votre CIN"
          value={cin}
          onChange={(e) => setCin(e.target.value)}
          required
          style={{ padding: 8, marginBottom: 10 }}
        />
        <br />
        <button type="submit">Commencer le test</button>
      </form>

      {message && (
        <pre
          style={{
            marginTop: 20,
            background: "#eee",
            padding: 10,
            borderRadius: 6,
          }}
        >
          {message}
        </pre>
      )}
    </div>
  );
}
