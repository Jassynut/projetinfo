"use client"
import { useNavigate, useLocation } from "react-router-dom"
import "../styles/Pages.css"

function TestSuccess() {
  const navigate = useNavigate()
  const location = useLocation()
  const score = location.state?.score || 0
  const totalQuestions = location.state?.totalQuestions || 21
  const cin = location.state?.cin || "John Doe"

  const handleDownloadCertificate = () => {
    // Mock certificate download
    alert("Téléchargement du certificat en cours...")
  }

  return (
    <div className="page-container">
      <div className="success-card">
        <div className="success-border">
          <div className="icon-circle success">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"></path>
            </svg>
          </div>

          <h1 className="success-title">Félicitations, [Nom Prénom] !</h1>

          <p className="success-message">
            Vous avez réussi le test HSE avec un score de {score} sur {totalQuestions}.
          </p>

          <p className="certificate-message">Votre certificat est prêt à être téléchargé.</p>

          <button onClick={handleDownloadCertificate} className="btn btn-primary btn-lg">
            Télécharger le certificat
          </button>
        </div>
      </div>
    </div>
  )
}

export default TestSuccess
