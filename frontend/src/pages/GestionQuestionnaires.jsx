import { useNavigate } from "react-router-dom";
import TopNav from "../components/TopNav";

export default function GestionQuestionnaires() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-10">
      <TopNav className="mb-4" />
      {/* Header */}
      <div className="flex justify-between items-center mb-12">
        <div className="flex items-center gap-3">
          <img src="/ocp-logo.png" alt="logo" className="w-12" />
          <h1 className="text-xl font-bold text-green-900">
            Induction HSE - Jorf Lasfar
          </h1>
        </div>

        <a href="/dashboard" className="text-green-700 font-semibold hover:underline">
          Accueil
        </a>
      </div>

      {/* Title */}
      <h2 className="text-3xl font-bold text-green-800 text-center mb-16">
        Gérer les questionnaires
      </h2>

      {/* Cards */}
      <div className="flex justify-center gap-12">

        {/* Gérer les versions */}
        <div
          onClick={() => navigate("/gerer-versions")}
          className="cursor-pointer bg-white w-80 p-10 rounded-xl shadow-lg border border-green-200 hover:shadow-xl transition text-center"
        >
          <img src="/icon-version.png" className="w-12 mx-auto mb-4" />
          <h3 className="text-green-700 text-xl font-semibold mb-2">Gérer les versions</h3>
          <p className="text-gray-600">
            Créer, modifier ou organiser les différentes versions du test HSE.
          </p>
        </div>

        {/* Gérer les questions */}
        <div
          onClick={() => navigate("/gerer-questions")}
          className="cursor-pointer bg-white w-80 p-10 rounded-xl shadow-lg border border-green-200 hover:shadow-xl transition text-center"
        >
          <img src="/icon-questions.png" className="w-12 mx-auto mb-4" />
          <h3 className="text-green-700 text-xl font-semibold mb-2">Gérer les questions</h3>
          <p className="text-gray-600">
            Ajouter, modifier ou supprimer des questions disponibles pour les versions.
          </p>
        </div>

      </div>

      {/* Footer */}
      <p className="text-center text-gray-600 mt-20">
        © 2025 OCP – Portail Interne HSE. Tous droits réservés.
      </p>
    </div>
  );
}
