"use client"

import { useState } from "react"
import "../styles/Tables.css"

const QuestionnairesList = () => {
  const [questions] = useState([
    { id: 1, title: "Question 1 : Exemple de question HSE.", required: true, actions: ["Supprimer"] },
    { id: 2, title: "Question 2 : Exemple de question HSE.", required: false, actions: ["Supprimer"] },
    { id: 3, title: "Question 3 : Exemple de question HSE.", required: true, actions: ["Supprimer"] },
    { id: 4, title: "Question 4 : Exemple de question HSE.", required: false, actions: ["Supprimer"] },
    { id: 5, title: "Question 5 : Exemple de question HSE.", required: true, actions: ["Supprimer"] },
  ])

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>Liste des questions</h2>
        <button className="btn-primary">+ Ajouter une question</button>
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Question</th>
            <th>Question Obligatoire</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {questions.map((q) => (
            <tr key={q.id}>
              <td>{q.id}</td>
              <td>{q.title}</td>
              <td className="checkbox-cell">
                <input type="checkbox" checked={q.required} readOnly />
              </td>
              <td>
                <span className="action-delete">Supprimer</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default QuestionnairesList
