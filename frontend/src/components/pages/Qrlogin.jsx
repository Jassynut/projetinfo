import { useParams } from "react-router-dom"
import { useState } from "react"

export default function QrLogin({ onQrLogin }) {
  const { testId } = useParams()
  const [cin, setCin] = useState("")
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    const result = await onQrLogin(cin, testId)

    if (!result.success) {
      setError(result.error)
    } else {
      window.location.href = result.redirectTo
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Authentification - Test #{testId}</h1>
      <p>Entrez votre CIN pour commencer le test.</p>

      <form onSubmit={handleSubmit}>
        <input
          value={cin}
          onChange={(e) => setCin(e.target.value)}
          placeholder="Votre CIN"
          style={{ padding: 10, width: "70%" }}
          required
        />
        <button style={{ padding: 10, marginLeft: 10 }}>Continuer</button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  )
}
