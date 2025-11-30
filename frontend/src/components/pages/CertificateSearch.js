"use client"

import { useState } from "react"
import "../styles/Form.css"

const CertificateSearch = () => {
  const [cin, setCin] = useState("")

  const handleSearch = (e) => {
    e.preventDefault()
    console.log("Searching for CIN:", cin)
  }

  return (
    <div className="page-container search-container">
      <div className="search-card">
        <h2>Consulter les certificats</h2>
        <p>Entrez le code CIN de l'apparenant pour afficher ses certificats HSE.</p>

        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Entrez le code CIN"
            value={cin}
            onChange={(e) => setCin(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="btn-primary">
            Rechercher
          </button>
        </form>
      </div>
    </div>
  )
}

export default CertificateSearch
