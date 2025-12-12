import { useState } from "react";
import axios from "axios";
import TopNav from "../components/TopNav";

const API_BASE = "http://127.0.0.1:8000";
const CNI_REGEX = /^[A-Z]{1,2}\d{5,6}$/i;

export default function ConsultationCertificats() {
  const [cni, setCni] = useState("");
  const [userInfo, setUserInfo] = useState(null);
  const [certificats, setCertificats] = useState([]);
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
    setUserInfo(null);
    setCertificats([]);
    
    try {
      const res = await axios.post(`${API_BASE}/api/certificats/recherche/`, {
        cni: value,
      });
      
      if (res.data.success) {
        setUserInfo(res.data.user_info);
        setCertificats(res.data.certificats || []);
        
        if (res.data.certificats.length === 0) {
          setError("Aucun certificat trouvé pour cet apprenant.");
        }
      } else {
        setError(res.data.error || "Erreur de recherche");
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setError("Aucun apprenant trouvé avec ce CNI.");
      } else {
        setError("Erreur lors de la recherche. Vérifiez votre connexion.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (attemptId) => {
    try {
      const response = await axios.get(
        `${API_BASE}/api/certificats/${attemptId}/pdf/`,
        {
          responseType: "blob",
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `certificat-hse-${attemptId}.pdf`
      );
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
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            className="bg-green-700 text-white px-6 py-3 rounded-lg shadow hover:bg-green-800"
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? "Recherche..." : "Rechercher"}
          </button>
        </div>
        
        {error && (
          <div className={`mb-4 p-3 rounded-lg ${error.includes("Aucun") ? "bg-yellow-50 text-yellow-800" : "bg-red-50 text-red-800"}`}>
            {error}
          </div>
        )}

        {/* Informations de l'apprenant */}
        {userInfo && (
          <div className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
            <h2 className="text-lg font-semibold text-green-800 mb-2">Informations de l'apprenant</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              <p><span className="font-medium">Nom complet:</span> {userInfo.full_name}</p>
              <p><span className="font-medium">CNI:</span> {maskCni(userInfo.cin)}</p>
              <p><span className="font-medium">Entreprise:</span> {userInfo.entreprise}</p>
              <p><span className="font-medium">Entité:</span> {userInfo.entite}</p>
            </div>
          </div>
        )}

        {/* Liste des certificats */}
        <div className="mt-6">
          {loading && (
            <div className="text-center py-4">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-700"></div>
              <p className="mt-2 text-gray-600">Recherche en cours...</p>
            </div>
          )}
          
          {!loading && certificats.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-green-800 mb-4">
                Certificats disponibles ({certificats.length})
              </h3>
              <div className="space-y-4">
                {certificats.map((cert) => (
                  <div
                    key={cert.id}
                    className="border rounded-lg p-4 bg-white hover:bg-green-50 transition-colors"
                  >
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                      <div className="mb-3 md:mb-0">
                        <div className="flex items-center gap-3 mb-2">
                          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                          <p className="font-semibold text-green-800">
                            Test HSE - Version {cert.test_version}
                          </p>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm text-gray-600">
                          <p>Date: {new Date(cert.date_test).toLocaleDateString('fr-FR')}</p>
                          <p>Score: {cert.score_sur_21}/21 ({Math.round(cert.score)}%)</p>
                          <p>Durée: {cert.time_taken_minutes} min</p>
                        </div>
                      </div>
                      <button
                        className="bg-green-700 hover:bg-green-800 text-white px-4 py-2 rounded-lg shadow transition-colors flex items-center gap-2"
                        onClick={() => handleDownload(cert.id)}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Télécharger
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function maskCni(value = "") {
  if (!value || value.length <= 2) return "***";
  return value.slice(0, 2) + "*".repeat(value.length - 3) + value.slice(-1);
}