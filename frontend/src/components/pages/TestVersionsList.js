"use client"

import { useState } from "react"
import "../styles/Tables.css"

const TestVersionsList = () => {
  const [versions] = useState([
    { id: 1, name: "Version 1", questions: 21, date: "01/10/2025", actions: ["Modifier", "Supprimer"] },
    { id: 2, name: "Version 2", questions: 21, date: "03/10/2025", actions: ["Modifier", "Supprimer"] },
    { id: 3, name: "Version 3", questions: 21, date: "05/10/2025", actions: ["Modifier", "Supprimer"] },
    { id: 4, name: "Version 4", questions: 21, date: "07/10/2025", actions: ["Modifier", "Supprimer"] },
    { id: 5, name: "Version 5", questions: 21, date: "09/10/2025", actions: ["Modifier", "Supprimer"] },
    { id: 6, name: "Version 6", questions: 21, date: "11/10/2025", actions: ["Modifier", "Supprimer"] },
  ])

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>Versions du Test HSE</h2>
        <p>Retrouvez ici les différentes versions du test HSE, chacune comportant 21 questions.</p>
        <button className="btn-primary">Nouvelle version</button>
      </div>

      <table className="data-table versions-table">
        <thead>
          <tr>
            <th>Nom de la version</th>
            <th>Nombre de questions</th>
            <th>Date de création</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {versions.map((v) => (
            <tr key={v.id}>
              <td>{v.name}</td>
              <td>{v.questions}</td>
              <td>{v.date}</td>
              <td>
                <span className="action-link">Modifier</span>
                <span className="action-delete">Supprimer</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default TestVersionsList
