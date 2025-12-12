import { useNavigate } from "react-router-dom";
import TopNav from "../components/TopNav";
export default function Dashboard() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-8">
      <TopNav className="mb-4" />
      {/* Header */}
      <header className="flex items-center gap-3 mb-12">
        <img src="/ocp-logo.png" alt="Logo OCP" className="w-12" />
        <h1 className="text-2xl font-bold text-green-900">
          Induction HSE - Jorf Lasfar
        </h1>
      </header>

      {/* Intro text */}
      <p className="text-center text-gray-700 text-xl font-medium max-w-4xl mx-auto mb-16 leading-relaxed">
        Ce portail vous permet de gérer les <span className="font-bold">formations HSE</span>, 
        les <span className="font-bold">tests</span>, et les 
        <span className="font-bold">certificats</span> de vos collaborateurs
        en toute simplicité.
      </p>

      {/* GRID CENTREE */}
      <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12">

        {/* CARD 1 */}
        <div
          onClick={() => navigate("/database")}
          className="cursor-pointer bg-white rounded-xl shadow-lg p-8 border border-green-200 hover:shadow-xl transition text-center"
        >
          <h2 className="text-green-700 text-xl font-semibold mb-5">Base de données</h2>
          <div className="w-24 h-24 mx-auto flex items-center justify-center">
            <img src="/data.png" className="max-w-full max-h-full object-contain" />
          </div>
        </div>


        {/* CARD 2 */}
        <div
          onClick={() => navigate("/hse-dashboard")}
          className="bg-white rounded-xl shadow-lg p-8 border border-green-200 hover:shadow-xl transition text-center">
          <h2 className="text-green-700 text-xl font-semibold mb-5">Tableau de bord</h2>
          <div className="w-24 h-24 mx-auto flex items-center justify-center">
            <img src="/stats.png" className="max-w-full max-h-full object-contain" />
          </div>
        </div>

        {/* CARD 3 */}
        <div
          onClick={() => navigate("/gestion-questionnaires")}
          className="cursor-pointer bg-white rounded-xl shadow-lg p-8 border border-green-200 hover:shadow-xl transition text-center"
        >
          <h2 className="text-green-700 text-xl font-semibold mb-5">Gestion des questionnaires</h2>
          <div className="w-24 h-24 mx-auto flex items-center justify-center">
            <img src="/question.png" className="max-w-full max-h-full object-contain" />
          </div>
        </div>


        {/* CARD 4 */}
        <div
          onClick={() => navigate("/test/selection")}
          className="cursor-pointer bg-white rounded-xl shadow-lg p-8 border border-green-200 hover:shadow-xl transition text-center">
          <h2 className="text-green-700 text-xl font-semibold mb-5">Commencer le test</h2>
          <div className="w-28 h-28 mx-auto flex items-center justify-center">
            <img src="/test.png" className="max-w-full max-h-full object-contain" />
          </div>
        </div>

        {/* CARD 5 LARGE */}
        <div
          onClick={() => navigate("/certificats")}
          className="cursor-pointer bg-white rounded-xl shadow-lg p-8 border border-green-200 hover:shadow-xl transition text-center md:col-span-2">
          <h2 className="text-green-700 text-xl font-semibold mb-5">Générer un certificat</h2>
          <div className="w-24 h-24 mx-auto flex items-center justify-center">
            <img src="/certificate.png" className="max-w-full max-h-full object-contain" />
          </div>
        </div>

      </div>

      {/* Footer */}
      <footer className="text-center mt-20 text-gray-600 text-sm">
        ©2025 OCP – Portail Interne HSE. Tous droits réservés.
      </footer>

    </div>
  );
}
