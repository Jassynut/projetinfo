import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import QRCode from "react-qr-code";
import TopNav from "../components/TopNav";

export default function CommencerTest() {
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const versionId = useMemo(() => localStorage.getItem("selectedTestVersion"), []);
  const origin = useMemo(() => window.location.origin, []);
  const qrValue = versionId ? `${origin}/test/${versionId}/passer` : "";

  const handleStartHere = () => {
    if (!versionId) {
      setError("Veuillez d'abord sélectionner une version de test.");
      return;
    }
    navigate(`/test/${versionId}/passer`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-8 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg border border-green-200 p-8 w-full max-w-lg">
        <TopNav className="mb-4" />
        <div className="flex items-center gap-3 mb-6">
          <img src="/ocp-logo.png" alt="logo" className="w-12" />
          <div>
            <h1 className="text-2xl font-bold text-green-900">Commencer le test</h1>
            <p className="text-sm text-gray-700">
              Scannez le QR pour ouvrir le test sur l’appareil de l’apprenant, ou démarrez ici.
            </p>
          </div>
        </div>

        {error && <p className="text-red-600 mb-3">{error}</p>}

        <div className="mt-6 space-y-3">
          <button
            className="w-full bg-blue-600 text-white py-3 rounded-lg shadow hover:bg-blue-700"
            onClick={handleStartHere}
          >
            Commencer le test sur cet appareil
          </button>
          {qrValue && (
            <div className="border rounded-lg p-4 text-center bg-gray-50">
              <p className="font-semibold text-green-800 mb-2">Scanner pour ouvrir sur un autre appareil</p>
              <div className="flex justify-center">
                <QRCode value={qrValue} size={180} />
              </div>
              <p className="text-xs text-gray-600 mt-2 break-words">{qrValue}</p>
            </div>
          )}
        </div>

        <p className="text-xs text-gray-600 mt-6">
          Si vous rencontrez un problème, contactez le responsable HSE.
        </p>
      </div>
    </div>
  );
}

