import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API_BASE } from "../config";
import TopNav from "../components/TopNav";

export default function GestionAdmins() {
  const navigate = useNavigate();
  const [managers, setManagers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingManager, setEditingManager] = useState(null);
  const [form, setForm] = useState({
    full_name: "",
    cin: "",
  });

  useEffect(() => {
    fetchManagers();
  }, []);

  const fetchManagers = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_BASE}/api/hse/managers/`, {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (res.data && Array.isArray(res.data)) {
        setManagers(res.data);
      } else if (res.data?.results) {
        setManagers(res.data.results);
      } else {
        setManagers([]);
      }
    } catch (err) {
      console.error("Erreur lors du chargement des managers:", err);
      if (err.response?.status === 403) {
        setError(
          "Accès refusé. Vous devez être connecté en tant que manager pour voir cette page. Veuillez vous connecter depuis la page d'accueil."
        );
      } else {
        setError(
          `Impossible de charger les managers: ${
            err.response?.data?.error || err.response?.data?.detail || err.message || "Erreur inconnue"
          }`
        );
      }
      setManagers([]);
    } finally {
      setLoading(false);
    }
  };

  const openCreate = () => {
    setEditingManager(null);
    setForm({ full_name: "", cin: "" });
    setShowModal(true);
    setError("");
    setSuccess("");
  };

  const openEdit = (manager) => {
    setEditingManager(manager);
    setForm({
      full_name: manager.full_name || "",
      cin: manager.cin || "",
    });
    setShowModal(true);
    setError("");
    setSuccess("");
  };

  const handleSave = async () => {
    if (!form.full_name.trim()) {
      setError("Le nom complet est obligatoire.");
      return;
    }
    if (!form.cin.trim()) {
      setError("Le CIN est obligatoire.");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const payload = {
        full_name: form.full_name.trim(),
        cin: form.cin.trim().toUpperCase(),
      };

      if (editingManager) {
        const res = await axios.put(
          `${API_BASE}/api/hse/managers/${editingManager.id}/`,
          payload,
          {
            withCredentials: true,
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        setSuccess("Manager modifié avec succès.");
      } else {
        const res = await axios.post(`${API_BASE}/api/hse/managers/`, payload, {
          withCredentials: true,
          headers: {
            "Content-Type": "application/json",
          },
        });
        setSuccess("Manager créé avec succès.");
      }
      setShowModal(false);
      fetchManagers();
    } catch (err) {
      console.error(err);
      if (err.response?.status === 401 || err.response?.status === 403) {
        setError("Vous devez être connecté en tant que manager pour modifier ou créer des managers. Veuillez vous connecter depuis la page d'accueil.");
      } else {
        const errorMsg =
          err.response?.data?.error ||
          err.response?.data?.detail ||
          err.response?.data?.cin?.[0] ||
          "Échec de l'enregistrement du manager.";
        setError(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (managerId) => {
    const ok = window.confirm(
      "Êtes-vous sûr de vouloir supprimer ce manager ? Cette action est irréversible."
    );
    if (!ok) return;
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await axios.delete(`${API_BASE}/api/hse/managers/${managerId}/`, {
        withCredentials: true,
      });
      setSuccess("Manager supprimé avec succès.");
      fetchManagers();
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.error ||
          err.response?.data?.detail ||
          "Échec de la suppression."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-8">
      <TopNav className="mb-4" />
      
      <div className="flex items-center justify-between mb-10">
        <div className="flex items-center gap-3">
          <img src="/ocp-logo.png" alt="logo" className="w-12" />
          <div>
            <h1 className="text-2xl font-bold text-green-900">
              Gérer les admins
            </h1>
            <p className="text-sm text-gray-700">
              Ajoutez ou modifiez les managers ayant accès à toutes les
              fonctionnalités de l'application.
            </p>
          </div>
        </div>
        <button
          onClick={() => navigate("/dashboard")}
          className="text-green-700 font-semibold hover:underline px-4 py-2 bg-white rounded-lg border border-green-200 hover:bg-green-50"
        >
          Retour au Dashboard
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-lg border border-green-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-green-800">
            Liste des managers
          </h2>
          <button
            onClick={openCreate}
            className="bg-green-700 text-white px-4 py-2 rounded-lg shadow hover:bg-green-800 transition"
          >
            + Ajouter un manager
          </button>
        </div>

        {error && !showModal && (
          <div className="mb-4 p-3 bg-red-50 border border-red-300 rounded-lg text-red-800">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 p-3 bg-green-50 border border-green-300 rounded-lg text-green-800">
            {success}
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-green-50 text-green-700 font-semibold">
                <th className="p-3 border">Nom complet</th>
                <th className="p-3 border">CIN</th>
                <th className="p-3 border text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading && !showModal && (
                <tr>
                  <td colSpan="3" className="p-4 text-center text-gray-500">
                    <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-green-700"></div>
                    <p className="mt-2">Chargement des managers...</p>
                  </td>
                </tr>
              )}
              {!loading &&
                managers.length > 0 &&
                managers.map((manager) => (
                  <tr key={manager.id} className="hover:bg-green-50">
                    <td className="p-3 border">{manager.full_name || "—"}</td>
                    <td className="p-3 border">{manager.cin || "—"}</td>
                    <td className="p-3 border text-center space-x-2">
                      <button
                        onClick={() => openEdit(manager)}
                        className="px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700 transition"
                      >
                        Modifier
                      </button>
                      <button
                        onClick={() => handleDelete(manager.id)}
                        className="px-3 py-1 rounded bg-red-600 text-white hover:bg-red-700 transition"
                      >
                        Supprimer
                      </button>
                    </td>
                  </tr>
                ))}
              {!loading && managers.length === 0 && (
                <tr>
                  <td colSpan="3" className="p-4 text-center text-gray-500">
                    Aucun manager disponible. Cliquez sur "Ajouter un manager"
                    pour en ajouter un.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
          <div className="bg-white w-full max-w-lg rounded-xl p-6 shadow-xl">
            <h3 className="text-xl font-semibold text-green-800 mb-4">
              {editingManager
                ? "Modifier le manager"
                : "Ajouter un nouveau manager"}
            </h3>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-300 rounded-lg text-red-800 text-sm">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block font-medium mb-1 text-gray-700">
                  Nom complet <span className="text-red-500">*</span>
                </label>
                <input
                  className="w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={form.full_name}
                  onChange={(e) =>
                    setForm({ ...form, full_name: e.target.value })
                  }
                  placeholder="Ex: Fatima Zohra"
                />
              </div>
              <div>
                <label className="block font-medium mb-1 text-gray-700">
                  CIN <span className="text-red-500">*</span>
                </label>
                <input
                  className="w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-green-500 uppercase"
                  value={form.cin}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      cin: e.target.value.toUpperCase(),
                    })
                  }
                  placeholder="Ex: AB123456"
                  maxLength={50}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Le CIN doit être unique et sera converti en majuscules.
                </p>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                className="px-4 py-2 rounded border border-gray-300 hover:bg-gray-50 transition"
                onClick={() => {
                  setShowModal(false);
                  setError("");
                }}
                disabled={loading}
              >
                Annuler
              </button>
              <button
                className="px-4 py-2 rounded bg-green-700 text-white hover:bg-green-800 transition disabled:opacity-50"
                onClick={handleSave}
                disabled={loading}
              >
                {loading ? "Enregistrement..." : "Enregistrer"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

