"use client"

import { useState } from "react"
import "../styles/Form.css"

const CertificateSearch = () => {
  const [cin, setcin] = useState("")

  const handleSearch = (e) => {
    e.preventDefault()
    console.log("Searching for cin:", cin)
  }

  return (
    <div className="page-container search-container">
      <div className="search-card">
        <h2>Consulter les certificats</h2>
        <p>Entrez le code cin de l'apparenant pour afficher ses certificats HSE.</p>

        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Entrez le code cin"
            value={cin}
            onChange={(e) => setcin(e.target.value)}
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
