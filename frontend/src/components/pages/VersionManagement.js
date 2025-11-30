"use client"

import { useState } from "react"
import "../styles/Tables.css"

const VersionManagement = () => {
  const [versions] = useState([
    { id: 1, title: "Question 1 : Exemple de question HSE.", action: "Supprimer" },
    { id: 2, title: "Question 2 : Exemple de question HSE.", action: "Supprimer" },
    { id: 3, title: "Question 3 : Exemple de question HSE.", action: "Supprimer" },
  ])

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>Modifier Version 1</h2>
        <button className="btn-link">← Retour</button>
      </div>

      <div className="version-list">
        {versions.map((v, index) => (
          <div key={index} className="version-item">
            <span>
              {v.id}. {v.title}
            </span>
            <span className="action-delete">{v.action}</span>
          </div>
        ))}
      </div>

      <div className="add-section">
        <h3>Ajouter une question existante</h3>
        <div className="add-form">
          <select className="form-input">
            <option>-- Sélectionner une question --</option>
          </select>
          <button className="btn-primary">Ajouter</button>
        </div>
      </div>

      <div className="form-actions">
        <button className="btn-link">Annuler</button>
        <button className="btn-success">Enregistrer</button>
      </div>
    </div>
  )
}

export default VersionManagement
