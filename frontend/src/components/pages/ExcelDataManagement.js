"use client"

import { useState } from "react"
import "../styles/Tables.css"

const ExcelDataManagement = () => {
  const [agents] = useState([
    {
      entity: "Entité 1",
      company: "Entreprise A",
      projectChief: "Chef A",
      name: "Nom Agent",
      surname: "Prénom",
      cin: "123456789",
      email: "agent@email.com",
      coordinatorEmail: "coord@email.com",
      function: "Fonction",
      attendance: "Présent",
      score: "85",
    },
  ])

  return (
    <div className="page-container">
      <div className="excel-header">
        <h2>Fichiers Excel</h2>
        <p>Choisissez la date et la table à consulter.</p>
        <div className="date-filter">
          <input type="text" placeholder="JJ" className="date-input" />
          <input type="text" placeholder="MM" className="date-input" />
          <input type="text" placeholder="AAAA" className="date-input" />
          <button className="btn-primary">Voir</button>
        </div>
        <a href="#" className="data-link">
          ⚙ Données des Agents
        </a>
      </div>

      <h3>Table des données</h3>
      <button className="btn-primary">+ Ajouter un agent</button>

      <table className="data-table excel-table">
        <thead>
          <tr>
            <th>Entité</th>
            <th>Entreprise</th>
            <th>Chef de Projet OCP</th>
            <th>Nom</th>
            <th>Prénom</th>
            <th>cin N°</th>
            <th>Adresse E-mail du Coordinateur</th>
            <th>Fonction de l'Agent</th>
            <th>Présence</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {agents.map((agent, idx) => (
            <tr key={idx}>
              <td>{agent.entity}</td>
              <td>{agent.company}</td>
              <td>{agent.projectChief}</td>
              <td>{agent.name}</td>
              <td>{agent.surname}</td>
              <td>{agent.cin}</td>
              <td>{agent.email}</td>
              <td>{agent.coordinatorEmail}</td>
              <td>{agent.function}</td>
              <td>{agent.attendance}</td>
              <td>{agent.score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default ExcelDataManagement
