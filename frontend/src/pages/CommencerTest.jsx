import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";
const CNI_REGEX = /^[A-Z]{1,2}\d{5,6}$/i;

export default function CommencerTest() {
  const [cni, setCni] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async () => {
    const versionId = localStorage.getItem("selectedTestVersion");
    if (!versionId) {
      setError("Veuillez d'abord sélectionner une version de test.");
      return;
    }
    const value = cni.trim().toUpperCase();
    if (!CNI_REGEX.test(value)) {
      setError("Format CNI invalide (ex: AE112456)");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/api/test/verifier-cni`, { cni: value });
      sessionStorage.setItem("cni", value);
      navigate(`/test/${versionId}/passer`);
    } catch (err) {
      setError("CNI non trouvée ou erreur de vérification.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-8 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg border border-green-200 p-8 w-full max-w-lg">
        <div className="flex items-center gap-3 mb-6">
          <img src="/ocp-logo.png" alt="logo" className="w-12" />
          <div>
            <h1 className="text-2xl font-bold text-green-900">Commencer le test</h1>
            <p className="text-sm text-gray-700">
              Entrez votre numéro de CNI pour démarrer le test sélectionné.
            </p>
          </div>
        </div>

        <label className="block font-medium mb-2">Numéro de CNI</label>
        <input
          className="w-full border rounded-lg p-3 mb-2"
          placeholder="AE112456"
          value={cni}
          onChange={(e) => setCni(e.target.value)}
        />
        <p className="text-sm text-gray-500 mb-4">Format attendu : lettres + chiffres (ex: AE112456)</p>

        {error && <p className="text-red-600 mb-3">{error}</p>}

        <button
          className="w-full bg-green-700 text-white py-3 rounded-lg shadow hover:bg-green-800"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Vérification..." : "Commencer le test"}
        </button>

        <p className="text-xs text-gray-600 mt-6">
          Si vous rencontrez un problème, contactez le responsable HSE.
        </p>
      </div>
    </div>
  );
}

