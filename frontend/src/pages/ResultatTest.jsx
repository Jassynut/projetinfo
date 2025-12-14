import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import TopNav from "../components/TopNav";

const API_BASE = "http://127.0.0.1:8000";

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
      const res = await axios.get(`${API_BASE}/api/test/${id}/resultat`);
      setData(res.data || {});
    } catch (err) {
      setError("Impossible de récupérer le résultat.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    const certId =
      data?.certificat_id || data?.certificate_id || data?.certificat?.id || data?.certificate?.id;
    if (!certId) {
      setError("Certificat non disponible.");
      return;
    }
    try {
      const res = await axios.get(`${API_BASE}/api/certificats/${certId}/pdf`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `certificat-${certId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError("Impossible de télécharger le certificat.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-8 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg border border-green-200 p-8 w-full max-w-3xl text-center">
        <TopNav className="mb-4" />
        {loading && <p className="text-gray-600">Chargement...</p>}
        {error && <p className="text-red-600 mb-3">{error}</p>}

        {data && !loading && (
          <>
            <h1 className="text-3xl font-bold text-green-900 mb-4">
              Félicitations {data?.user_name || "!"}
            </h1>
            <p className="text-lg text-gray-700 mb-6">
              Vous avez réussi le test HSE avec un score de{" "}
              <span className="font-semibold text-green-800">
                {data?.score ?? data?.note ?? data?.points ?? "—"}/21
              </span>
            </p>

            <div className="flex flex-col md:flex-row md:justify-center gap-3 mb-6">
              {/* Afficher le bouton de téléchargement uniquement si le test est réussi */}
              {/* Le test est réussi si passed=true ou si toutes les questions obligatoires sont correctes (9/9) */}
              {(data?.passed === true || data?.mandatory_correct >= 9 || (data?.mandatory_correct === data?.mandatory_total && data?.mandatory_total > 0)) && (
                <button
                  className="bg-blue-600 text-white px-5 py-3 rounded-lg shadow hover:bg-blue-700"
                  onClick={handleDownload}
                >
                  Télécharger le certificat
                </button>
              )}
              <button
                className="bg-green-700 text-white px-5 py-3 rounded-lg shadow hover:bg-green-800"
                onClick={() => navigate("/test/selection")}
              >
                {data?.passed === true ? "Revenir à la sélection" : "Revenir à la sélection"}
              </button>
            </div>

            <p className="text-sm text-gray-600">
              Version du test : {data?.test_version || data?.version || id}
            </p>
            <p className="text-sm text-gray-600">
              Tentative : {data?.attempt_id || data?.id || "—"}
            </p>
          </>
        )}
      </div>
    </div>
  );
}

