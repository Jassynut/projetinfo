import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API_BASE } from "../config";

export default function Login() {

  const [fullName, setFullName] = useState("");
  const [cin, setCin] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (!fullName.trim() || !cin.trim()) {
      setError("Veuillez remplir tous les champs");
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(
        `${API_BASE}/manager/login/`,
        {
          full_name: fullName.trim(),
          cin: cin.trim().toUpperCase()
        },
        {
          withCredentials: true, // Important pour les cookies de session
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        // Connexion réussie → on sauvegarde l'état dans localStorage
        localStorage.setItem("loggedIn", "true");
        localStorage.setItem("userType", "manager");
        localStorage.setItem("userData", JSON.stringify(response.data.user));
        navigate("/dashboard");
      } else {
        setError(response.data.error || "Identifiants incorrects");
      }
    } catch (err) {
      console.error("Erreur de connexion:", err);
      setError(
        err.response?.data?.error || 
        "Erreur de connexion. Vérifiez vos identifiants (Nom complet + CIN)."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-green-300">
      <div className="text-center w-full max-w-md px-6">

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
            <label className="font-medium">Nom complet</label>
            <input
              type="text"
              placeholder="ex: Fatima Zohra"
              className="w-full mt-1 px-4 py-2 border rounded-lg bg-white"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="text-left">
            <label className="font-medium">CIN</label>
            <input
              type="text"
              placeholder="ex: AB123456"
              className="w-full mt-1 px-4 py-2 border rounded-lg bg-white uppercase"
              value={cin}
              onChange={(e) => setCin(e.target.value.toUpperCase())}
              disabled={loading}
            />
          </div>

          {/* Button */}
          <button
            type="submit"
            className="w-full bg-green-700 hover:bg-green-800 text-white py-2 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={loading}
          >
            {loading ? "Connexion..." : "Se connecter"}
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
