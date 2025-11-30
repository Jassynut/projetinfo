"use client"

import { useState } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import "../styles/Pages.css"

function TestVersionSelection() {
  const [selectedVersion, setSelectedVersion] = useState(null)
  const navigate = useNavigate()
  const location = useLocation()
  const cin = location.state?.cin || ""

  const versions = ["Version 1", "Version 2", "Version 3", "Version 4", "Version 5", "Version 6"]

  const handleStartTest = () => {
    if (selectedVersion) {
      navigate("/test-taking", {
        state: { cin, version: selectedVersion },
      })
    }
  }

  return (
    <div className="page-container">
      <div className="card-centered">
        <div className="icon-circle">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
            <polyline points="13 2 13 9 20 9"></polyline>
          </svg>
        </div>

        <div className="card-title-large">Sélection du test HSE</div>
        <p className="card-subtitle">Choisissez la version du test à administrer</p>

        <div className="versions-grid">
          {versions.map((version) => (
            <button
              key={version}
              onClick={() => setSelectedVersion(version)}
              className={`version-card ${selectedVersion === version ? "selected" : ""}`}
            >
              {version}
            </button>
          ))}
        </div>

        <button onClick={handleStartTest} className="btn btn-primary btn-lg" disabled={!selectedVersion}>
          Commencer le test HSE
        </button>
      </div>
    </div>
  )
}

export default TestVersionSelection
