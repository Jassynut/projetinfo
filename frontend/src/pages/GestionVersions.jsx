import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { API_BASE } from "../config";

export default function GestionVersions() {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingVersion, setEditingVersion] = useState(null);
  const [form, setForm] = useState({
    name: "",
    description: "",
  });

  const sortedVersions = useMemo(
    () =>
      [...versions].sort(
        (a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)
      ),
    [versions]
  );

  useEffect(() => {
    fetchVersions();
  }, []);

  const fetchVersions = async () => {
    setLoading(true);
    setError("");
    try {
      // Récupérer toutes les versions (pas seulement les actives) pour la gestion
      // Essayer d'abord sans trailing slash, puis avec
      let resAll;
      try {
        resAll = await axios.get(`${API_BASE}/api/versions`);
      } catch (err) {
        try {
          resAll = await axios.get(`${API_BASE}/api/versions/`);
        } catch (err2) {
          throw err; // Re-throw la première erreur
        }
      }
      
      let items = resAll.data?.versions || resAll.data?.tests || resAll.data || [];
      
      // Si aucune version n'est trouvée, essayer les versions actives
      if (!items.length) {
        try {
          const resActives = await axios.get(`${API_BASE}/api/versions/actives`);
          items = resActives.data?.versions || [];
        } catch (err) {
          console.warn("Erreur lors de la récupération des versions actives:", err);
        }
      }
      
      // Normaliser les données
      items = items.map((v) => {
        // Calculer le nombre exact de questions depuis ordre_questions
        let questionsCount = 0;
        if (v.ordre_questions && Array.isArray(v.ordre_questions)) {
          questionsCount = v.ordre_questions.length;
        } else if (v.questions_count !== undefined) {
          questionsCount = v.questions_count;
        } else if (v.total_questions !== undefined) {
          questionsCount = v.total_questions;
        }
        
        return {
          ...v, 
          name: v.name || `Version ${v.version || ''}`,
          total_questions: questionsCount,
          questions_count: questionsCount,  // S'assurer que questions_count est défini
          created_at: v.created_at || v.createdAt || null
        };
      });
      
      console.log("Versions chargées:", items);
      setVersions(items);
    } catch (err) {
      console.error("Erreur lors du chargement des versions:", err);
      setError(`Impossible de charger les versions: ${err.response?.data?.error || err.message || "Erreur inconnue"}`);
      setVersions([]);
    } finally {
      setLoading(false);
    }
  };

  const openCreate = () => {
    setEditingVersion(null);
    setForm({ name: "", description: "" });
    setShowModal(true);
  };

  const openEdit = (version) => {
    setEditingVersion(version);
    setForm({
      name: version?.name || `Version ${version?.version || ""}`,
      description: version?.description || "",
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    if (!form.name.trim()) {
      setError("Le nom de la version est obligatoire.");
      return;
    }
    
    // Validation : Version doit être un entier positif
    const versionMatch = form.name.match(/Version\s*(\d+)/i);
    if (versionMatch) {
      const versionNum = parseInt(versionMatch[1]);
      if (versionNum < 1) {
        setError(`Version invalide. La version doit être un nombre entier positif (>= 1). Vous avez fourni : Version ${versionNum}`);
        return;
      }
    }
    
    setLoading(true);
    setError("");
    try {
      let response;
      if (editingVersion) {
        response = await axios.put(`${API_BASE}/api/versions/${editingVersion.id}`, {
          name: form.name,
          description: form.description,
        });
      } else {
        response = await axios.post(`${API_BASE}/api/versions`, {
          name: form.name,
          description: form.description,
        });
        // Afficher un message de succès si disponible
        if (response.data?.message) {
          alert(response.data.message);
        }
      }
      setShowModal(false);
      fetchVersions();
    } catch (err) {
      console.error(err);
      const errorMsg = err.response?.data?.error || "Échec de l'enregistrement de la version.";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (versionId) => {
    const ok = window.confirm("Supprimer cette version ?");
    if (!ok) return;
    setLoading(true);
    setError("");
    try {
      await axios.delete(`${API_BASE}/api/versions/${versionId}`);
      fetchVersions();
    } catch (err) {
      console.error(err);
      setError("Échec de la suppression.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-8">
      <div className="flex items-center justify-between mb-10">
        <div className="flex items-center gap-3">
          <img src="/ocp-logo.png" alt="logo" className="w-12" />
          <div>
            <h1 className="text-2xl font-bold text-green-900">Gestion des versions</h1>
            <p className="text-sm text-gray-700">
              Gérez les versions du test HSE.
            </p>
          </div>
        </div>
        <a href="/gestion-questionnaires" className="text-green-700 font-semibold hover:underline">
          Retour
        </a>
      </div>

      <div className="bg-white rounded-xl shadow-lg border border-green-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-green-800">Versions</h2>
          <button
            onClick={openCreate}
            className="bg-green-700 text-white px-4 py-2 rounded-lg shadow hover:bg-green-800"
          >
            + Créer une version
          </button>
        </div>

        {error && <p className="text-red-600 mb-4">{error}</p>}

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-green-50 text-green-700 font-semibold">
                <th className="p-3 border">Nom</th>
                <th className="p-3 border">Questions</th>
                <th className="p-3 border">Créé le</th>
                <th className="p-3 border text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan="4" className="p-4 text-center text-gray-500">
                    <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-green-700"></div>
                    <p className="mt-2">Chargement des versions...</p>
                  </td>
                </tr>
              )}
              {!loading && sortedVersions.length > 0 && sortedVersions.map((v) => (
                <tr key={v.id} className="hover:bg-green-50">
                  <td className="p-3 border">
                    {v.name || `Version ${v.version || v.id}`}
                  </td>
                  <td className="p-3 border">
                    {v.questions_count !== undefined && v.questions_count !== null 
                      ? v.questions_count 
                      : (v.ordre_questions && Array.isArray(v.ordre_questions) 
                        ? v.ordre_questions.length 
                        : (v.total_questions || 0))}
                  </td>
                  <td className="p-3 border">
                    {v.created_at
                      ? new Date(v.created_at).toLocaleDateString('fr-FR')
                      : "—"}
                  </td>
                  <td className="p-3 border text-center space-x-2">
                    <button
                      onClick={() => window.location.href = `/modifier-version/${v.id}`}
                      className="px-3 py-1 rounded bg-green-600 text-white hover:bg-green-700"
                    >
                      Modifier ordre
                    </button>
                    <button
                      onClick={() => openEdit(v)}
                      className="px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700"
                    >
                      Modifier
                    </button>
                    <button
                      onClick={() => handleDelete(v.id)}
                      className="px-3 py-1 rounded bg-red-600 text-white hover:bg-red-700"
                    >
                      Supprimer
                    </button>
                  </td>
                </tr>
              ))}
              {!loading && sortedVersions.length === 0 && (
                <tr>
                  <td colSpan="4" className="p-4 text-center text-gray-500">
                    Aucune version disponible. Cliquez sur "Créer une version" pour en ajouter une.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white w-full max-w-lg rounded-xl p-6 shadow-xl">
            <h3 className="text-xl font-semibold text-green-800 mb-4">
              {editingVersion ? "Modifier la version" : "Créer une version"}
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block font-medium mb-1">Nom de la version</label>
                <input
                  className="w-full border rounded-lg p-2"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="Ex: Version 1"
                />
              </div>
              <div>
                <label className="block font-medium mb-1">Description</label>
                <textarea
                  className="w-full border rounded-lg p-2"
                  rows={3}
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  placeholder="Détails sur cette version..."
                />
              </div>
              {!editingVersion && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
                  <p className="font-semibold mb-1">ℹ️ Information</p>
                  <p>Toutes les questions actives de la base de données seront automatiquement ajoutées à cette version. Vous pourrez ensuite modifier l'ordre par glisser-déposer dans la page de modification.</p>
                </div>
              )}
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                className="px-4 py-2 rounded border"
                onClick={() => setShowModal(false)}
              >
                Annuler
              </button>
              <button
                className="px-4 py-2 rounded bg-green-700 text-white"
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

