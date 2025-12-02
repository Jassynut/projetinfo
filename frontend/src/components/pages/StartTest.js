"use client"

import { useState } from "react"
import { useNavigate } from "react-router-dom"
import "../styles/Pages.css"

function StartTest() {
  const [cin, setcin] = useState("")
  const navigate = useNavigate()

  const handleStartTest = () => {
    if (cin.trim()) {
      navigate("/test-version-selection", { state: { cin } })
    }
  }

  return (
    <div className="page-container">
      <div className="card-centered">
        <div className="card-title-large">Démarrer le Test</div>
        <p className="card-subtitle">Veuillez saisir votre numéro de cin pour commencer.</p>

        <div className="form-group">
          <label>Numéro de cin :</label>
          <input
            type="text"
            placeholder="Ex : AB123456"
            value={cin}
            onChange={(e) => setcin(e.target.value)}
            className="input-field"
          />
        </div>

        <button onClick={handleStartTest} className="btn btn-primary btn-lg" disabled={!cin.trim()}>
          Commencer le test
        </button>

        <p className="help-text">Si vous rencontrez un problème, contactez le responsable HSE de votre entité.</p>
      </div>
    </div>
  )
}

export default StartTest
