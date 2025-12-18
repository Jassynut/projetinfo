import { useState, useEffect } from "react";
import axios from "axios";
import { API_BASE } from "../config";

// S'assurer que axios envoie les cookies de session
axios.defaults.withCredentials = true;
axios.defaults.headers.common['Content-Type'] = 'application/json';

export default function ManualEditStudent({ user, onSuccess, onClose }) {
  const [formData, setFormData] = useState({
    cin: "",
    nom: "",
    prenom: "",
    entite: "",
    entreprise: "",
    chef_projet_ocp: ""
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // Initialiser le formulaire avec les données de l'utilisateur
  useEffect(() => {
    if (user) {
      setFormData({
        cin: user.cin || "",
        nom: user.nom || "",
        prenom: user.prénom || user.prenom || "",
        entite: user.entite || "",
        entreprise: user.entreprise || "",
        chef_projet_ocp: user.chef_projet_ocp || ""
      });
    }
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    if (!formData.cin || !formData.nom || !formData.prenom) {
      setMessage("❌ Veuillez remplir au moins le CIN, le nom et le prénom.");
      setLoading(false);
      return;
    }

    if (!user || !user.id) {
      setMessage("❌ Erreur: Utilisateur non trouvé.");
      setLoading(false);
      return;
    }

    try {
      // Vérifier d'abord si l'utilisateur est authentifié
      const checkAuth = await axios.get(`${API_BASE}/api/auth/current-user/`, {
        withCredentials: true
      });
      
      if (!checkAuth.data?.user || !checkAuth.data.user.is_manager) {
        setMessage("❌ Vous devez être connecté en tant que manager pour modifier un apprenant.");
        setLoading(false);
        return;
      }

      // Utiliser l'endpoint de mise à jour dédié (même principe que create)
      const response = await axios.put(
        `${API_BASE}/api/hse/users/${user.id}/update/`,
        {
          cin: formData.cin.toUpperCase(),
          nom: formData.nom,
          prénom: formData.prenom,
          entite: formData.entite || '',
          entreprise: formData.entreprise || '',
          chef_projet_ocp: formData.chef_projet_ocp || ''
        },
        {
          withCredentials: true,
          headers: {
            'Content-Type': 'application/json',
          }
        }
      );

      if (response.data) {
        setMessage("✅ Apprenant modifié avec succès !");
        
        // Appeler le callback de succès si fourni
        if (onSuccess) {
          setTimeout(() => {
            onSuccess();
            if (onClose) onClose();
          }, 1000);
        }
      } else {
        setMessage(`❌ Erreur: ${response.data?.error || 'Erreur lors de la modification'}`);
      }
    } catch (error) {
      console.error("Erreur modification apprenant:", error);
      const errorMsg = error.response?.data?.error || error.response?.data?.detail || error.message || 'Erreur lors de la modification';
      setMessage(`❌ Erreur: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-green-900">Modifier un apprenant</h3>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
            type="button"
          >
            ✕
          </button>
        )}
      </div>
      
      {message && (
        <div className={`p-3 rounded mb-4 ${message.includes('✅') ? 'bg-green-100 text-green-700' : 
          message.includes('⚠️') ? 'bg-yellow-100 text-yellow-700' : 
          'bg-red-100 text-red-700'}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">CIN *</label>
          <input
            type="text"
            required
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Ex: AB123456"
            value={formData.cin}
            onChange={(e) => setFormData({...formData, cin: e.target.value.toUpperCase()})}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nom *</label>
            <input
              type="text"
              required
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Nom de famille"
              value={formData.nom}
              onChange={(e) => setFormData({...formData, nom: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Prénom *</label>
            <input
              type="text"
              required
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Prénom"
              value={formData.prenom}
              onChange={(e) => setFormData({...formData, prenom: e.target.value})}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Entité</label>
          <input
            type="text"
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Entité (optionnel)"
            value={formData.entite}
            onChange={(e) => setFormData({...formData, entite: e.target.value})}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Entreprise</label>
          <input
            type="text"
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Entreprise (optionnel)"
            value={formData.entreprise}
            onChange={(e) => setFormData({...formData, entreprise: e.target.value})}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Chef de projet OCP</label>
          <input
            type="text"
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Chef de projet (optionnel)"
            value={formData.chef_projet_ocp}
            onChange={(e) => setFormData({...formData, chef_projet_ocp: e.target.value})}
          />
        </div>

        <div className="flex gap-3 mt-6">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-green-700 text-white px-4 py-2 rounded-lg hover:bg-green-800 transition disabled:opacity-50"
          >
            {loading ? "Modification..." : "Modifier"}
          </button>
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition"
            >
              Annuler
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

