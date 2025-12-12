import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export default function SelectionTest() {
  const [versions, setVersions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
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
    localStorage.setItem("selectedTestVersion", selected.id || selected.version || "");
    navigate("/test/commencer");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-8">
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

