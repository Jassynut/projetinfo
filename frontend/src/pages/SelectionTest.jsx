import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import TopNav from "../components/TopNav";

import { API_BASE } from "../config";

export default function SelectionTest() {
  const [versions, setVersions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [etat, setEtat] = useState('test_final'); // État du test (initial ou final)
  const navigate = useNavigate();

  useEffect(() => {
    fetchVersions();
  }, []);

  const fetchVersions = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_BASE}/api/versions/actives`);
      setVersions(res.data?.versions || res.data?.tests || res.data || []);
    } catch (err) {
      setError("Impossible de charger les versions disponibles.");
    } finally {
      setLoading(false);
    }
  };

  const handleContinue = () => {
    if (!selected) {
      setError("Veuillez sélectionner une version.");
      return;
    }
    // S'assurer qu'on a un ID valide
    const testId = selected.id || selected.version || selected.test_id;
    if (!testId) {
      setError("Erreur: ID du test manquant. Veuillez réessayer.");
      console.error("Version sélectionnée sans ID:", selected);
      return;
    }
    console.log("Version sélectionnée:", selected);
    console.log("ID du test sauvegardé:", testId);
    console.log("État du test:", etat);
    localStorage.setItem("selectedTestVersion", String(testId));
    localStorage.setItem("selectedTestEtat", etat); // Stocker l'état choisi
    navigate("/test/commencer");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-8">
      <TopNav className="mb-4" />
      <div className="max-w-5xl mx-auto bg-white rounded-xl shadow-lg border border-green-200 p-8">
        <div className="flex items-center gap-3 mb-6">
          <img src="/ocp-logo.png" alt="logo" className="w-12" />
          <div>
            <h1 className="text-2xl font-bold text-green-900">Sélection du test HSE</h1>
            <p className="text-sm text-gray-700">
              Choisissez une version active puis passez à l’identification.
            </p>
          </div>
        </div>

        {error && <p className="text-red-600 mb-3">{error}</p>}

        {loading && <p className="text-gray-600">Chargement des versions...</p>}

        {/* Choix du type de test (Initial/Final) */}
        <div className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
          <label className="block text-green-700 font-semibold mb-3">
            Type de test :
          </label>
          <div className="flex gap-4">
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="etat"
                value="test_initial"
                checked={etat === 'test_initial'}
                onChange={(e) => setEtat(e.target.value)}
                className="mr-2 w-4 h-4 text-green-600 focus:ring-green-500"
              />
              <span className="text-gray-700">Test Initial</span>
            </label>
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="etat"
                value="test_final"
                checked={etat === 'test_final'}
                onChange={(e) => setEtat(e.target.value)}
                className="mr-2 w-4 h-4 text-green-600 focus:ring-green-500"
              />
              <span className="text-gray-700">Test Final</span>
            </label>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {etat === 'test_initial' 
              ? "Les tests initiaux ne génèrent pas de certificat." 
              : "Les tests finaux peuvent générer un certificat si réussi."}
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {versions.map((v) => {
            const isSelected = selected?.id === v.id;
            return (
              <div
                key={v.id}
                onClick={() => setSelected(v)}
                className={`cursor-pointer border rounded-xl p-4 shadow-sm hover:shadow-md transition ${
                  isSelected ? "border-green-600 ring-2 ring-green-300" : "border-green-200"
                }`}
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-green-800">
                    {v.name || `Version ${v.version}`}
                  </h3>
                  {isSelected && (
                    <span className="text-sm text-green-700 font-semibold">Sélectionnée</span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {v.description || "Version du test HSE - 21 questions"}
                </p>
              </div>
            );
          })}
          {!loading && versions.length === 0 && (
            <p className="text-gray-600">Aucune version active.</p>
          )}
        </div>

        <div className="mt-6 flex justify-end">
          <button
            className="bg-green-700 text-white px-6 py-3 rounded-lg shadow hover:bg-green-800"
            onClick={handleContinue}
          >
            Commencer
          </button>
        </div>
      </div>
    </div>
  );
}

