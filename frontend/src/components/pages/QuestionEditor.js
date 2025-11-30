"use client"

import { useState } from "react"
import "../styles/Form.css"

const QuestionEditor = () => {
  const [formData, setFormData] = useState({
    questionText: "",
    image: null,
    yesResponse: true,
    noResponse: false,
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleFileChange = (e) => {
    setFormData((prev) => ({ ...prev, image: e.target.files[0] }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    console.log("Question submitted:", formData)
  }

  return (
    <div className="page-container">
      <div className="form-header">
        <h2>Éditeur de questions</h2>
        <button className="btn-link">+ Retour</button>
      </div>

      <form className="form-card" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Texte de la question</label>
          <textarea
            name="questionText"
            value={formData.questionText}
            onChange={handleChange}
            placeholder="Entrez votre question ici..."
            rows="6"
          />
        </div>

        <div className="form-group">
          <label>Image (optionnelle)</label>
          <div className="file-input-wrapper">
            <input type="file" accept="image/*" onChange={handleFileChange} id="file-input" />
            <label htmlFor="file-input" className="file-label">
              Choose File {formData.image && `- ${formData.image.name}`}
            </label>
          </div>
        </div>

        <div className="form-group">
          <label>Réponse</label>
          <div className="response-buttons">
            <button type="button" className="btn-success">
              ✓ Oui
            </button>
            <button type="button" className="btn-danger">
              ✕ Non
            </button>
          </div>
        </div>

        <button type="submit" className="btn-primary">
          Ajouter la question
        </button>
      </form>
    </div>
  )
}

export default QuestionEditor
