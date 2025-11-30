"use client"
import { useNavigate } from "react-router-dom"
import "../styles/Pages.css"

function TestQRCode() {
  const navigate = useNavigate()
  const testUrl = "https://exemple.com/test"

  return (
    <div className="page-container">
      <button className="btn-back" onClick={() => navigate(-1)}>
        ← Retour
      </button>

      <div className="card-centered">
        <div className="icon-circle">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 11h8V3H3v8zm10 0h8V3h-8v8zM3 21h8v-8H3v8zm10 0h8v-8h-8v8z"></path>
          </svg>
        </div>

        <div className="card-title-large">Test version 1</div>
        <p className="card-subtitle">Scannez le QR code pour accéder au test</p>

        {/* Placeholder QR Code */}
        <div className="qr-code-placeholder">
          <svg width="200" height="200" viewBox="0 0 200 200" fill="none">
            <rect width="200" height="200" fill="white" />
            <rect x="15" y="15" width="50" height="50" fill="black" />
            <rect x="135" y="15" width="50" height="50" fill="black" />
            <rect x="15" y="135" width="50" height="50" fill="black" />
            <circle cx="100" cy="100" r="40" fill="black" />
            <circle cx="100" cy="100" r="30" fill="white" />
            <circle cx="100" cy="100" r="20" fill="black" />
          </svg>
        </div>

        <p className="test-url">{testUrl}</p>
      </div>
    </div>
  )
}

export default TestQRCode
