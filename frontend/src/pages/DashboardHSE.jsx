import { useEffect, useState } from "react";
import axios from "axios";
import TopNav from "../components/TopNav";
import { API_BASE } from "../config";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function DashboardHSE() {
  const [stats, setStats] = useState({
    presence: 0,
    test_initial: 0,
    test_final: 0,
    improvement: 0,
    total_users: 0,
    presence_count: 0,
    total_attempts: 0
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [date, setDate] = useState(() => {
    const today = new Date();
    return {
      day: today.getDate().toString().padStart(2, '0'),
      month: (today.getMonth() + 1).toString().padStart(2, '0'),
      year: today.getFullYear().toString()
    };
  });

  const [monthlyData, setMonthlyData] = useState(null);
  const [loadingMonthly, setLoadingMonthly] = useState(false);

  // Charger les données automatiquement au montage
  useEffect(() => {
    fetchData();
    fetchMonthlyData();
  }, []);

  // Fonction pour récupérer données du backend
  const fetchData = async (customDay = "", customMonth = "", customYear = "") => {
    setLoading(true);
    setError("");
    
    try {
      const day = customDay || date.day;
      const month = customMonth || date.month;
      const year = customYear || date.year;

      const baseURL = `${API_BASE}/api/stats/hse/stats/`;
      const params = { day, month, year };
      
      const response = await axios.get(baseURL, { params });

      if (response.status === 204 || response.data === "") {
        setError("Aucune donnée disponible pour cette date");
        resetStats();
        return;
      }

      let data = response.data;
      
      if (typeof data === 'string' && data.trim() !== '') {
        try {
          data = JSON.parse(data);
        } catch (e) {
          // Ignore parse errors
        }
      }

      if (!data) {
        setError("Format de données inattendu");
        resetStats();
        return;
      }

      let extractedData = data;
      
      if (data.data) {
        extractedData = data.data;
      } else if (data.results) {
        extractedData = data.results;
      } else if (Array.isArray(data) && data.length > 0) {
        extractedData = data[0];
      }

      const newStats = {
        presence: parseFloat(extractedData?.presence) || 
                  parseFloat(extractedData?.presence_percentage) || 
                  parseFloat(extractedData?.attendance_rate) || 0,
        
        test_initial: parseFloat(extractedData?.test_initial) || 
                     parseFloat(extractedData?.initial_test) || 
                     parseFloat(extractedData?.initial_score) || 
                     parseFloat(extractedData?.pretest) || 0,
        
        test_final: parseFloat(extractedData?.test_final) || 
                   parseFloat(extractedData?.final_test) || 
                   parseFloat(extractedData?.final_score) || 
                   parseFloat(extractedData?.posttest) || 0,
        
        improvement: parseFloat(extractedData?.improvement) || 
                    parseFloat(extractedData?.progress) || 
                    parseFloat(extractedData?.difference) || 0,
        
        total_users: parseInt(extractedData?.total_users) || 
                    parseInt(extractedData?.total_students) || 
                    parseInt(extractedData?.users_count) || 0,
        
        presence_count: parseInt(extractedData?.presence_count) || 
                       parseInt(extractedData?.attendance_count) || 
                       parseInt(extractedData?.present_students) || 0,
        
        total_attempts: parseInt(extractedData?.total_attempts) || 
                       parseInt(extractedData?.attempts_count) || 
                       parseInt(extractedData?.tests_taken) || 0
      };

      const allZero = Object.values(newStats).every(val => val === 0);
      if (allZero) {
        setError("Aucune donnée trouvée pour cette date. Vérifiez que des données existent pour le " + 
                `${day}/${month}/${year}`);
      }

      setStats(newStats);

    } catch (err) {
      if (err.response) {
        if (err.response.status === 404) {
          setError(`Endpoint non trouvé. Vérifiez que l'URL ${API_BASE}/api/stats/hse/stats/ est correcte`);
        } else if (err.response.status === 500) {
          setError("Erreur interne du serveur. Contactez l'administrateur");
        } else if (err.response.data?.detail) {
          setError(`Erreur serveur: ${err.response.data.detail}`);
        } else if (err.response.data?.error) {
          setError(`Erreur: ${err.response.data.error}`);
        } else {
          setError(`Erreur ${err.response.status}: ${err.response.statusText}`);
        }
      } else if (err.request) {
        setError("Impossible de contacter le serveur. Vérifiez votre connexion internet");
      } else {
        setError(`Erreur: ${err.message}`);
      }
      
      resetStats();
    } finally {
      setLoading(false);
    }
  };

  // Fonction pour récupérer les données mensuelles
  const fetchMonthlyData = async () => {
    setLoadingMonthly(true);
    try {
      const month = date.month;
      const year = date.year;
      const response = await axios.get(`${API_BASE}/api/stats/hse/stats/monthly/`, {
        params: { month, year }
      });
      
      if (response.data && response.data.data) {
        setMonthlyData(response.data.data);
      }
    } catch (err) {
      // Silently fail for monthly data
      console.error("Erreur récupération données mensuelles:", err);
    } finally {
      setLoadingMonthly(false);
    }
  };

  // Fonction pour réinitialiser les statistiques
  const resetStats = () => {
    setStats({
      presence: 0,
      test_initial: 0,
      test_final: 0,
      improvement: 0,
      total_users: 0,
      presence_count: 0,
      total_attempts: 0
    });
  };

  const handleVoir = async () => {
    if (!date.day || !date.month || !date.year) {
      setError("Veuillez remplir tous les champs");
      return;
    }

    await fetchData(date.day, date.month, date.year);
    await fetchMonthlyData();
  };

  const handleDateToday = () => {
    const today = new Date();
    const newDate = {
      day: today.getDate().toString().padStart(2, '0'),
      month: (today.getMonth() + 1).toString().padStart(2, '0'),
      year: today.getFullYear().toString()
    };
    
    setDate(newDate);
    fetchData(newDate.day, newDate.month, newDate.year);
    fetchMonthlyData();
  };

  const formatPercentage = (value) => {
    return `${Number(value).toFixed(2)}%`;
  };

  // Préparer les données pour le graphique
  const chartData = monthlyData ? {
    labels: monthlyData.map(item => `Jour ${item.day}`),
    datasets: [
      {
        label: 'Test Initial',
        data: monthlyData.map(item => item.test_initial),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Test Final',
        data: monthlyData.map(item => item.test_final),
        borderColor: 'rgb(147, 51, 234)',
        backgroundColor: 'rgba(147, 51, 234, 0.1)',
        tension: 0.4,
      },
    ],
  } : null;

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `Progression des moyennes - ${date.month}/${date.year}`,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        }
      },
    },
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-6 md:p-10">
      <TopNav className="mb-4" />
      
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-green-900 mb-2">
          Tableau de bord HSE
        </h1>
        <p className="text-gray-700">
          Statistiques détaillées pour le jour sélectionné
        </p>
      </div>

      {/* Sélecteur de date */}
      <div className="bg-white p-6 rounded-xl shadow-lg mb-8">
        <h2 className="text-xl font-semibold text-green-900 mb-4">Sélectionner une date</h2>
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex flex-col">
            <label className="text-sm text-gray-700 mb-1">Jour</label>
            <input
              type="number"
              min="1"
              max="31"
              className="w-20 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="JJ"
              value={date.day}
              onChange={e => setDate({ ...date, day: e.target.value.padStart(2, '0') })}
            />
          </div>
          <div className="flex flex-col">
            <label className="text-sm text-gray-700 mb-1">Mois</label>
            <input
              type="number"
              min="1"
              max="12"
              className="w-20 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="MM"
              value={date.month}
              onChange={e => setDate({ ...date, month: e.target.value.padStart(2, '0') })}
            />
          </div>
          <div className="flex flex-col">
            <label className="text-sm text-gray-700 mb-1">Année</label>
            <input
              type="number"
              min="2020"
              max="2100"
              className="w-24 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="AAAA"
              value={date.year}
              onChange={e => setDate({ ...date, year: e.target.value })}
            />
          </div>
          <button 
            className="bg-green-700 text-white px-6 py-2 rounded hover:bg-green-800 transition-colors font-semibold disabled:opacity-50"
            onClick={handleVoir}
            disabled={loading}
          >
            {loading ? "Chargement..." : "Voir les stats"}
          </button>
          <button 
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
            onClick={handleDateToday}
            disabled={loading}
          >
            Aujourd'hui
          </button>
        </div>
        <div className="mt-3 text-sm text-gray-600">
          <p>Date sélectionnée: {date.day}/{date.month}/{date.year}</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          <strong>Erreur :</strong> {error}
        </div>
      )}

      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-700"></div>
          <p className="mt-4 text-gray-700">Chargement des statistiques...</p>
        </div>
      )}

      {!loading && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-white p-6 rounded-xl shadow-lg text-center">
              <div className="flex items-center justify-center mb-4">
                <div className="bg-green-100 p-3 rounded-full">
                  <svg className="w-8 h-8 text-green-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
              </div>
              <h2 className="text-lg font-semibold text-gray-700 mb-2">Présences</h2>
              <p className="text-5xl font-bold text-green-700 mb-2">
                {formatPercentage(stats.presence)}
              </p>
              <p className="text-sm text-gray-600">
                {stats.presence_count} / {stats.total_users} apprenants
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-lg text-center">
              <div className="flex items-center justify-center mb-4">
                <div className="bg-blue-100 p-3 rounded-full">
                  <svg className="w-8 h-8 text-blue-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
              <h2 className="text-lg font-semibold text-gray-700 mb-2">Test Initial</h2>
              <p className="text-5xl font-bold text-blue-700 mb-2">
                {formatPercentage(stats.test_initial)}
              </p>
              <p className="text-sm text-gray-600">
                Score moyen au début
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-lg text-center">
              <div className="flex items-center justify-center mb-4">
                <div className="bg-purple-100 p-3 rounded-full">
                  <svg className="w-8 h-8 text-purple-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                  </svg>
                </div>
              </div>
              <h2 className="text-lg font-semibold text-gray-700 mb-2">Test Final</h2>
              <p className="text-5xl font-bold text-purple-700 mb-2">
                {formatPercentage(stats.test_final)}
              </p>
              <p className="text-sm text-gray-600">
                Score moyen à la fin
              </p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg mb-8">
            <h2 className="text-2xl font-bold text-green-900 mb-6">Détails des statistiques</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg border">
                <p className="text-sm text-gray-600">Amélioration</p>
                <p className="text-2xl font-bold text-green-700">
                  {stats.improvement > 0 ? '+' : ''}{formatPercentage(stats.improvement)}
                </p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg border">
                <p className="text-sm text-gray-600">Total Apprenants</p>
                <p className="text-2xl font-bold text-blue-700">{stats.total_users}</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg border">
                <p className="text-sm text-gray-600">Présents</p>
                <p className="text-2xl font-bold text-green-700">{stats.presence_count}</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg border">
                <p className="text-sm text-gray-600">Tentatives Tests</p>
                <p className="text-2xl font-bold text-purple-700">{stats.total_attempts}</p>
              </div>
            </div>
          </div>

          {/* Graphique de progression mensuelle */}
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <h2 className="text-2xl font-bold text-green-900 mb-6">
              Progression des moyennes - Mois de {date.month}/{date.year}
            </h2>
            
            {loadingMonthly ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-700"></div>
                <p className="mt-4 text-gray-700">Chargement du graphique...</p>
              </div>
            ) : chartData ? (
              <div className="h-96">
                <Line data={chartData} options={chartOptions} />
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>Aucune donnée disponible pour ce mois</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
