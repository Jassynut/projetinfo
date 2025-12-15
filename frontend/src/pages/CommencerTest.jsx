import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import QRCode from "react-qr-code";
import TopNav from "../components/TopNav";
import { API_BASE } from "../config";

export default function CommencerTest() {
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const versionId = useMemo(() => localStorage.getItem("selectedTestVersion"), []);
  
  // Construire l'URL pour le QR code - TOUJOURS utiliser l'IP locale pour que les téléphones puissent y accéder
  const getFrontendUrl = () => {
    // Toujours utiliser l'IP locale pour que les téléphones puissent y accéder
    const currentPort = window.location.port;
    const isDevMode = currentPort === '5173' || currentPort === ''; // Vite dev server ou Docker
    
    // Déterminer le port du frontend
    let frontendPort = '3000'; // Port Docker par défaut
    if (isDevMode && currentPort === '5173') {
      frontendPort = '5173'; // Mode développement local
    }
    
    // Extraire l'IP du backend ou utiliser l'IP locale par défaut
    try {
      const apiUrl = new URL(API_BASE);
      const backendHost = apiUrl.hostname;
      
      // Si l'API utilise localhost, utiliser l'IP locale par défaut
      if (backendHost === 'localhost' || backendHost === '127.0.0.1') {
        return `http://10.24.159.24:${frontendPort}`;
      }
      // Sinon utiliser le même hostname que le backend
      return `http://${backendHost}:${frontendPort}`;
    } catch (e) {
      // Fallback : utiliser l'IP locale par défaut (IP de la machine)
      return `http://10.24.159.24:${frontendPort}`;
    }
  };
  
  const frontendUrl = useMemo(() => getFrontendUrl(), []);
  const qrValue = versionId ? `${frontendUrl}/test/${versionId}/passer` : "";
  
  // Afficher l'URL dans la console pour déboguer
  useEffect(() => {
    if (qrValue) {
      console.log('🔗 QR Code URL générée:', qrValue);
      console.log('📱 Testez cette URL sur votre téléphone:', qrValue);
      console.log('💡 Assurez-vous que votre téléphone est sur le même réseau Wi-Fi');
    }
  }, [qrValue]);

  const handleStartHere = () => {
    if (!versionId) {
      setError("Veuillez d'abord sélectionner une version de test.");
      return;
    }
    console.log("Navigation vers le test avec ID:", versionId);
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
              <p className="text-xs text-gray-600 mt-2 break-words font-mono">{qrValue}</p>
              <p className="text-xs text-blue-600 mt-2">
                ⚠️ Assurez-vous que votre téléphone est sur le même réseau Wi-Fi
              </p>
            </div>
          )}
          {!qrValue && (
            <div className="border rounded-lg p-4 text-center bg-yellow-50">
              <p className="text-yellow-800 text-sm">
                ⚠️ Aucune version sélectionnée. Veuillez d'abord sélectionner une version de test.
              </p>
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

