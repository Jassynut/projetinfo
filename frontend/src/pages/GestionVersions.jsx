import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import TopNav from "../components/TopNav";

const API_BASE = "http://127.0.0.1:8000";

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
      const res = await axios.get(`${API_BASE}/api/versions`);
      setVersions(res.data?.versions || res.data?.tests || res.data || []);
    } catch (err) {
      console.error(err);
      setError("Impossible de charger les versions.");
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
    setLoading(true);
    setError("");
    try {
      if (editingVersion) {
        await axios.put(`${API_BASE}/api/versions/${editingVersion.id}`, {
          name: form.name,
          description: form.description,
        });
      } else {
        await axios.post(`${API_BASE}/api/versions`, {
          name: form.name,
          description: form.description,
        });
      }
      setShowModal(false);
      fetchVersions();
    } catch (err) {
      console.error(err);
      setError("Échec de l’enregistrement de la version.");
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
      <TopNav className="mb-4" />
      <div className="flex items-center justify-between mb-10">
        <div className="flex items-center gap-3">
          <img src="/ocp-logo.png" alt="logo" className="w-12" />
          <div>
            <h1 className="text-2xl font-bold text-green-900">Gestion des versions</h1>
            <p className="text-sm text-gray-700">
              Gérez les versions du test HSE (21 questions par version).
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
              {sortedVersions.map((v) => (
                <tr key={v.id} className="hover:bg-green-50">
                  <td className="p-3 border">
                    {v.name || `Version ${v.version}`}
                  </td>
                  <td className="p-3 border">
                    {v.total_questions || v.totalQuestions || 21}
                  </td>
                  <td className="p-3 border">
                    {v.created_at
                      ? new Date(v.created_at).toLocaleDateString()
                      : "—"}
                  </td>
                  <td className="p-3 border text-center space-x-2">
                    <button
                      onClick={() => openEdit(v)}
                      className="px-3 py-1 rounded bg-blue-600 text-white"
                    >
                      Modifier
                    </button>
                    <button
                      onClick={() => handleDelete(v.id)}
                      className="px-3 py-1 rounded bg-red-600 text-white"
                    >
                      Supprimer
                    </button>
                  </td>
                </tr>
              ))}
              {!loading && sortedVersions.length === 0 && (
                <tr>
                  <td colSpan="4" className="p-4 text-center text-gray-500">
                    Aucune version disponible.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          {loading && <p className="text-center py-4 text-gray-600">Chargement...</p>}
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
                  placeholder="Détails sur cette version (21 questions)..."
                />
              </div>
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

