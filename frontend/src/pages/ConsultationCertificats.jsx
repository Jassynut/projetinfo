import { useState } from "react";
import axios from "axios";
import TopNav from "../components/TopNav";

const API_BASE = "http://127.0.0.1:8000";
const CNI_REGEX = /^[A-Z]{1,2}\d{5,6}$/i;

export default function ConsultationCertificats() {
  const [cni, setCni] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    const value = cni.trim().toUpperCase();
    if (!CNI_REGEX.test(value)) {
      setError("Format CNI invalide (ex: AE112456)");
      return;
    }
    setError("");
    setLoading(true);
    setResults([]);
    try {
      const res = await axios.post(`${API_BASE}/api/certificats/recherche`, {
        cni: value,
      });
      setResults(res.data?.certificats || res.data?.certificates || []);
    } catch (err) {
      setError("Aucun certificat trouvé ou erreur de recherche.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (id) => {
    try {
      const res = await axios.get(`${API_BASE}/api/certificats/${id}/pdf`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `certificat-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError("Impossible de télécharger le certificat.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-8">
      <TopNav className="mb-4" />
      <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-lg border border-green-200 p-8">
        <div className="flex items-center gap-3 mb-6">
          <img src="/ocp-logo.png" alt="logo" className="w-12" />
          <div>
            <h1 className="text-2xl font-bold text-green-900">Consultation des certificats</h1>
            <p className="text-sm text-gray-700">
              Recherchez un certificat HSE à partir du code CNI.
            </p>
          </div>
        </div>

        <div className="flex flex-col md:flex-row gap-3 mb-4">
          <input
            className="flex-1 border rounded-lg p-3"
            placeholder="Entrez le code CNI (ex: AE112456)"
            value={cni}
            onChange={(e) => setCni(e.target.value)}
          />
          <button
            className="bg-green-700 text-white px-6 py-3 rounded-lg shadow hover:bg-green-800"
            onClick={handleSearch}
            disabled={loading}
          >
            Rechercher
          </button>
        </div>
        {error && <p className="text-red-600 mb-2">{error}</p>}

        <div className="mt-6">
          {loading && <p className="text-gray-600">Recherche en cours...</p>}
          {!loading && results.length === 0 && (
            <p className="text-gray-600">Aucun résultat pour le moment.</p>
          )}
          {results.length > 0 && (
            <div className="space-y-4">
              {results.map((item) => (
                <div
                  key={item.id}
                  className="border rounded-lg p-4 flex flex-col md:flex-row md:items-center md:justify-between"
                >
                  <div>
                    <p className="font-semibold text-green-800">
                      {item.user_full_name || item.nom || "Apprenant"}
                    </p>
                    <p className="text-sm text-gray-600">
                      CNI : {item.user_cin ? maskCni(item.user_cin) : "—"}
                    </p>
                    <p className="text-sm text-gray-600">
                      Test version : {item.test_version || item.version || "—"} — Score :{" "}
                      {item.score ?? item.note ?? "—"}/21
                    </p>
                    <p className="text-sm text-gray-600">
                      Date :{" "}
                      {item.issued_date
                        ? new Date(item.issued_date).toLocaleDateString()
                        : "—"}
                    </p>
                  </div>
                  <button
                    className="mt-3 md:mt-0 bg-blue-600 text-white px-4 py-2 rounded-lg shadow hover:bg-blue-700"
                    onClick={() => handleDownload(item.id)}
                  >
                    Télécharger le certificat
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function maskCni(value = "") {
  if (value.length <= 2) return "*".repeat(value.length);
  return value.slice(0, 2) + "*".repeat(Math.max(0, value.length - 3)) + value.slice(-1);
}

