"use client"

import { useState } from "react"
import "../styles/Login.css"

const Login = ({ onLogin }) => {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const handleSubmit = (e) => {
    e.preventDefault()
    onLogin(email, password)
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-logo">
          <img
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Ccircle cx='20' cy='20' r='18' fill='%2310b981' opacity='0.1'/%3E%3Cpath d='M20 8 L25 15 L30 12 L32 18 L26 20 L30 26 L24 23 L20 30 L16 23 L10 26 L14 20 L8 18 L14 12 L15 15 Z' fill='%2310b981'/%3E%3C/svg%3E"
            alt="OCP"
          />
        </div>
        <h1>Induction HSE - Jorf Lasfar</h1>
        <p>Connectez-vous à votre espace</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Nom d'utilisateur</label>
            <input
              type="text"
              placeholder="ex: Titie admin"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Mot de passe</label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn-login">
            Se connecter
          </button>
        </form>

        <p className="footer-text">© 2025 OCP - Portail interne HSE. Tous droits réservés.</p>
      </div>
    </div>
  )
}

export default Login
