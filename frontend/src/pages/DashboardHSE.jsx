import { useEffect, useState } from "react";
import axios from "axios";

export default function DashboardHSE() {
  const [presence, setPresence] = useState(null);
  const [initialTest, setInitialTest] = useState(null);
  const [finalTest, setFinalTest] = useState(null);
  const [date, setDate] = useState({ day: "", month: "", year: "" });

  // Charger les données du jour automatiquement
  useEffect(() => {
    fetchData();
  }, []);

  // Fonction pour récupérer données du backend
  const fetchData = async (d = "", m = "", y = "") => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/stats/hse/stats/", {
        params: { day: d, month: m, year: y }
      });

      setPresence(response.data.presence);
      setInitialTest(response.data.test_initial);
      setFinalTest(response.data.test_final);

    } catch (err) {
      console.error(err);
      alert("Aucune donnée pour cette date.");
    }
  };

  const handleVoir = () => {
    fetchData(date.day, date.month, date.year);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-10">
      
      <h1 className="text-3xl font-bold text-green-900 mb-10">
        Tableau de bord HSE
      </h1>

      {/* Sélecteur de date */}
      <div className="flex gap-3 mb-10">
        <input
          className="w-20 p-2 border rounded"
          placeholder="JJ"
          onChange={e => setDate({ ...date, day: e.target.value })}
        />
        <input
          className="w-20 p-2 border rounded"
          placeholder="MM"
          onChange={e => setDate({ ...date, month: e.target.value })}
        />
        <input
          className="w-24 p-2 border rounded"
          placeholder="AAAA"
          onChange={e => setDate({ ...date, year: e.target.value })}
        />
        <button className="bg-green-700 text-white px-4 rounded" onClick={handleVoir}>
          Voir
        </button>
      </div>

      {/* Cartes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">

        {/* Présence */}
        <div className="bg-white p-8 rounded-xl shadow text-center">
          <h2 className="text-xl font-semibold mb-4">Pourcentage de présences</h2>
          <p className="text-5xl font-bold text-green-700">
            {presence !== null ? presence + "%" : "..."}
          </p>
        </div>

        {/* Tests */}
        <div className="bg-white p-8 rounded-xl shadow">
          <h2 className="text-xl font-semibold mb-4 text-center">
            Comparaison test initial / test final
          </h2>

          {/* Barres */}
          <p>Test initial</p>
          <div className="bg-gray-200 h-3 rounded mb-4">
            <div
              className="bg-green-600 h-3 rounded"
              style={{ width: initialTest + "%" }}
            ></div>
          </div>

          <p>Test final</p>
          <div className="bg-gray-200 h-3 rounded mb-4">
            <div
              className="bg-green-600 h-3 rounded"
              style={{ width: finalTest + "%" }}
            ></div>
          </div>

          {initialTest !== null && finalTest !== null && (
            <p className="text-center text-gray-700">
              Amélioration : {finalTest - initialTest} points
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
