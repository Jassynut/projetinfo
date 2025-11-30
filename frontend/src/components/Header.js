"use client"
import { Link } from "react-router-dom"
import "./Header.css"

const Header = ({ onLogout }) => {
  return (
    <header className="header">
      <div className="header-container">
        <div className="logo-section">
          <img
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Ccircle cx='20' cy='20' r='18' fill='%2310b981' opacity='0.1'/%3E%3Cpath d='M20 8 L25 15 L30 12 L32 18 L26 20 L30 26 L24 23 L20 30 L16 23 L10 26 L14 20 L8 18 L14 12 L15 15 Z' fill='%2310b981'/%3E%3C/svg%3E"
            alt="OCP"
            className="logo"
          />
          <h1>Induction HSE - Jorf Lasfar</h1>
        </div>
        <nav className="header-nav">
          <Link to="/">Accueil</Link>
        </nav>
        <button onClick={onLogout} className="logout-btn">
          Déconnexion
        </button>
      </div>
    </header>
  )
}

export default Header
