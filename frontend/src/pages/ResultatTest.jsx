import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import TopNavLearner from "../components/TopNavLearner";

import { API_BASE } from "../config";

export default function ResultatTest() {
  const { id } = useParams(); // test id
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchResult();
  }, [id]);

  const fetchResult = async () => {
    setLoading(true);
    setError("");
    try {
      // D'abord, essayer de récupérer depuis sessionStorage (données fraîches de la soumission)
      const storedResult = sessionStorage.getItem('testResult');
      if (storedResult) {
        try {
          const parsedResult = JSON.parse(storedResult);
          console.log("Données depuis sessionStorage:", parsedResult);
          setData(parsedResult);
          sessionStorage.removeItem('testResult'); // Nettoyer après utilisation
          setLoading(false);
          return;
        } catch (e) {
          console.error("Erreur parsing sessionStorage:", e);
        }
      }
      
      // Sinon, récupérer depuis l'API
      const res = await axios.get(`${API_BASE}/api/test/${id}/resultat`);
      const resultData = res.data || {};
      console.log("Données depuis API:", resultData);
      setData(resultData);
    } catch (err) {
      console.error("Erreur récupération résultat:", err);
      setError("Impossible de récupérer le résultat.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    const certId = data?.certificate_id || data?.certificat_id || data?.certificat?.id || data?.certificate?.id;
    const attemptId = data?.attempt_id;
    const cin = data?.cin || sessionStorage.getItem("cni") || "";
    
    console.log("Données pour téléchargement:", { certId, attemptId, cin, data });
    
    if (!attemptId) {
      setError("Informations de tentative manquantes. Impossible de générer le certificat.");
      return;
    }
    
    if (!cin) {
      setError("CIN manquant. Impossible de générer le certificat.");
      return;
    }
    
    try {
      let downloadUrl;
      
      // Toujours utiliser le format cert::{cin}::test::{attempt_id} pour générer le certificat à la volée
      // Cela garantit que le certificat sera généré même s'il n'est pas dans la base de données
      downloadUrl = `${API_BASE}/api/certificats/cert::${cin}::test::${attemptId}/pdf`;
      
      console.log("Téléchargement depuis:", downloadUrl);
      setError(""); // Effacer les erreurs précédentes
      
      const res = await axios.get(downloadUrl, {
        responseType: "blob",
      });
      
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      const fileName = `certificat-hse-${cin}-${attemptId}.pdf`;
      link.setAttribute("download", fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Erreur téléchargement certificat:", err);
      console.error("Détails:", err.response?.data);
      const errorMsg = err.response?.data?.error || err.message || "Impossible de télécharger le certificat.";
      setError(`Erreur: ${errorMsg}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-8 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg border border-green-200 p-8 w-full max-w-3xl text-center">
        <TopNavLearner className="mb-4" />
        {loading && <p className="text-gray-600">Chargement...</p>}
        {error && <p className="text-red-600 mb-3">{error}</p>}

        {data && !loading && (
          <>
            {data?.passed === true ? (
              <>
                <h1 className="text-3xl font-bold text-green-900 mb-4">
                  Test terminé
                </h1>
                <p className="text-lg text-gray-700 mb-6">
                  Score obtenu :{" "}
                  <span className="font-semibold text-green-800">
                    {data?.score ?? data?.note ?? data?.points ?? "—"}/{data?.total_questions ?? 21}
                  </span>
                </p>

                <div className="flex flex-col md:flex-row md:justify-center gap-3 mb-6">
                  {/* Afficher le bouton de téléchargement si le test est réussi (certificat généré automatiquement) */}
                  {data?.passed === true && (
                    <button
                      className="bg-blue-600 text-white px-5 py-3 rounded-lg shadow hover:bg-blue-700 flex items-center gap-2"
                      onClick={handleDownload}
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Télécharger le certificat
                    </button>
                  )}
                  <button
                    className="bg-gray-500 text-white px-5 py-3 rounded-lg shadow hover:bg-gray-600"
                    onClick={() => {
                      alert("Merci d'avoir passé le test. Vous pouvez fermer cette page.");
                    }}
                  >
                    Fermer
                  </button>
                </div>
              </>
            ) : (
              <>
                <h1 className="text-3xl font-bold text-red-600 mb-4">
                  Test échoué
                </h1>
                <p className="text-lg text-gray-700 mb-6">
                  Score obtenu :{" "}
                  <span className="font-semibold text-red-800">
                    {data?.score ?? data?.note ?? data?.points ?? "—"}/{data?.total_questions ?? 21}
                  </span>
                </p>
                <p className="text-gray-600 mb-6">
                  Vous n'avez pas réussi toutes les questions obligatoires. Veuillez réessayer.
                </p>
                <div className="flex flex-col md:flex-row md:justify-center gap-3 mb-6">
                  <button
                    className="bg-gray-500 text-white px-5 py-3 rounded-lg shadow hover:bg-gray-600"
                    onClick={() => {
                      alert("Merci d'avoir passé le test. Vous pouvez fermer cette page.");
                    }}
                  >
                    Fermer
                  </button>
                </div>
              </>
            )}

            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                Version du test : {data?.test_version || data?.version || id}
              </p>
              <p className="text-sm text-gray-600">
                Tentative : {data?.attempt_id || data?.id || "—"}
              </p>
              {data?.mandatory_correct !== undefined && (
                <p className="text-sm text-gray-600">
                  Questions obligatoires : {data?.mandatory_correct}/{data?.mandatory_total || 0}
                </p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

