import { useState } from "react";
import { useNavigate } from "react-router-dom";
import TopNav from "../components/TopNav";

export default function Login() {

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  // 🔥 Les identifiants autorisés (modifiable quand tu veux)
  const VALID_USERNAME = "admin";
  const VALID_PASSWORD = "1234";

  const handleSubmit = (e) => {
    e.preventDefault();

    if (username === VALID_USERNAME && password === VALID_PASSWORD) {
      // Connexion réussie → on sauvegarde l'état dans localStorage
      localStorage.setItem("loggedIn", "true");
      navigate("/dashboard");
    } else {
      setError("Nom d’utilisateur ou mot de passe incorrect !");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-green-300">
      <div className="text-center w-full max-w-md px-6">
        <TopNav className="mb-4" />

        {/* Logo */}
        <img
          src="/ocp-logo.png"
          alt="OCP Logo"
          className="w-20 mx-auto mb-4"
        />

        {/* Title */}
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Induction HSE - Jorf Lasfar
        </h1>

        <p className="text-gray-600 mb-8">Connectez-vous à votre espace</p>

        {/* Form */}
        <form className="space-y-4" onSubmit={handleSubmit}>

          <div className="text-left">
            <label className="font-medium">Nom d’utilisateur</label>
            <input
              type="text"
              placeholder="ex: hse.admin"
              className="w-full mt-1 px-4 py-2 border rounded-lg bg-white"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          <div className="text-left">
            <label className="font-medium">Mot de passe</label>
            <input
              type="password"
              placeholder="••••••••"
              className="w-full mt-1 px-4 py-2 border rounded-lg bg-white"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {/* Button */}
          <button
            type="submit"
            className="w-full bg-green-700 hover:bg-green-800 text-white py-2 rounded-lg font-semibold"
          >
            Se connecter
          </button>

          {/* 🔥 Message d’erreur */}
          {error && <p className="text-red-600 mt-2">{error}</p>}

        </form>

        {/* Footer */}
        <p className="text-xs text-gray-600 mt-10">
          ©2025 OCP – Portail Interne HSE. Tous droits réservés.
        </p>
      </div>
    </div>
  );
}
