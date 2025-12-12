import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import TopNav from "../components/TopNav";

const API_BASE = "http://127.0.0.1:8000";

export default function GestionQuestions() {
  const [questions, setQuestions] = useState([]);
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);
  const [form, setForm] = useState({
    question_code: "",
    enonce_fr: "",
    enonce_ar: "",
    enonce_en: "",
    categorie: "",
    reponse_correcte: true,
    image: null,
    version_id: "",
  });

  const orderedQuestions = useMemo(
    () =>
      [...questions].sort((a, b) => {
        const numA = parseInt(a.question_code?.replace(/\D/g, "") || "0", 10);
        const numB = parseInt(b.question_code?.replace(/\D/g, "") || "0", 10);
        return numA - numB;
      }),
    [questions]
  );

  useEffect(() => {
    fetchQuestions();
    fetchVersions();
  }, []);

  const fetchQuestions = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_BASE}/api/questions/`);
      // Ajuste selon la structure de ta réponse API
      setQuestions(res.data?.questions || res.data || []);
    } catch (err) {
      setError("Impossible de charger les questions.");
    } finally {
      setLoading(false);
    }
  };

  const fetchVersions = async () => {
    try {
      const resActives = await axios.get(`${API_BASE}/api/versions/actives`);
      let items = resActives.data?.versions || [];
      if (!items.length) {
        const resAll = await axios.get(`${API_BASE}/api/versions`);
        items = resAll.data?.versions || resAll.data?.tests || resAll.data || [];
      }
      items = items.map((v) => ({ ...v, name: v.name || `Version ${v.version}` }));
      setVersions(items);
    } catch (err) {
      setVersions([]);
    }
  };

  const openCreate = () => {
    setEditingQuestion(null);
    setForm({
      question_code: "",
      enonce_fr: "",
      enonce_ar: "",
      enonce_en: "",
      categorie: "",
      reponse_correcte: true,
      image: null,
      version_id: "",
    });
    setShowModal(true);
  };

  const openEdit = (q) => {
    setEditingQuestion(q);
    setForm({
      question_code: q.question_code || "",
      enonce_fr: q.enonce_fr || "",
      enonce_ar: q.enonce_ar || "",
      enonce_en: q.enonce_en || "",
      categorie: q.categorie || "",
      reponse_correcte: !!q.reponse_correcte,
      image: null,
      version_id: q.version_id || "",
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    if (!form.enonce_fr.trim()) {
      setError("Le texte de la question est obligatoire.");
      return;
    }
    if (!form.question_code.trim()) {
      setError("Le code question est obligatoire (ex: Q1).");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const payload = new FormData();
      payload.append("question_code", form.question_code);
      payload.append("enonce_fr", form.enonce_fr);
      payload.append("enonce_ar", form.enonce_ar || "");
      payload.append("enonce_en", form.enonce_en || "");
      payload.append("reponse_correcte", form.reponse_correcte);
      payload.append("is_mandatory", false); // Ajoute si nécessaire
      payload.append("points", 1); // Ajoute si nécessaire

      // Ajouter l'image uniquement si elle est sélectionnée
      if (form.image) {
        payload.append("image", form.image);
      }

      let questionId = null;

      if (editingQuestion) {
        // Pour PUT, envoie toutes les données
        const response = await axios.put(
          `${API_BASE}/api/questions/${editingQuestion.id}/`,
          payload,
          {
            headers: { "Content-Type": "multipart/form-data" },
          }
        );
        questionId = editingQuestion.id;
      } else {
        // Pour POST, crée une nouvelle question
        const response = await axios.post(
          `${API_BASE}/api/questions/`,
          payload,
          {
            headers: { "Content-Type": "multipart/form-data" },
          }
        );
        questionId = response.data?.id || editingQuestion?.id;
      }

      // Associer à une version si fournie
      if (form.version_id && questionId) {
        try {
          await axios.post(`${API_BASE}/api/versions/${form.version_id}/questions/add`, {
            question_id: questionId
          });
        } catch (assocError) {
          console.warn("Association échouée, mais question créée:", assocError);
          // Continue même si l'association échoue
        }
      }

      setShowModal(false);
      fetchQuestions();
    } catch (err) {
      console.error("Erreur:", err.response?.data || err.message);
      setError("Échec de l'enregistrement. " + (err.response?.data?.error || ""));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    const ok = window.confirm("Supprimer cette question ?");
    if (!ok) return;

    setLoading(true);
    setError("");
    try {
      await axios.delete(`${API_BASE}/api/questions/${id}/`);
      fetchQuestions();
    } catch (err) {
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
            <h1 className="text-2xl font-bold text-green-900">Gestion des questions</h1>
            <p className="text-sm text-gray-700">Banque de 21 questions Oui/Non.</p>
          </div>
        </div>
        <a href="/gestion-questionnaires" className="text-green-700 font-semibold hover:underline">
          Retour
        </a>
      </div>

      <div className="bg-white rounded-xl shadow-lg border border-green-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-green-800">Questions</h2>
          <button
            onClick={openCreate}
            className="bg-green-700 text-white px-4 py-2 rounded-lg shadow hover:bg-green-800"
          >
            + Ajouter une question
          </button>
        </div>

        {error && <p className="text-red-600 mb-4">{error}</p>}

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-green-50 text-green-700 font-semibold">
                <th className="p-3 border">Code</th>
                <th className="p-3 border">Question (FR)</th>
                <th className="p-3 border">Question (AR)</th>
                <th className="p-3 border">Question (EN)</th>
                <th className="p-3 border">Réponse correcte</th>
                <th className="p-3 border text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {orderedQuestions.map((q, idx) => (
                <tr key={q.id || idx} className="hover:bg-green-50">
                  <td className="p-3 border font-semibold">{q.question_code || `Q${idx + 1}`}</td>
                  <td className="p-3 border">{q.enonce_fr}</td>
                  <td className="p-3 border">{q.enonce_ar || "-"}</td>
                  <td className="p-3 border">{q.enonce_en || "-"}</td>
                  <td className="p-3 border">{q.reponse_correcte ? "Oui" : "Non"}</td>
                  <td className="p-3 border text-center space-x-2">
                    <button
                      onClick={() => openEdit(q)}
                      className="px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700"
                    >
                      Éditer
                    </button>
                    <button
                      onClick={() => handleDelete(q.id)}
                      className="px-3 py-1 rounded bg-red-600 text-white hover:bg-red-700"
                    >
                      Supprimer
                    </button>
                  </td>
                </tr>
              ))}
              {!loading && orderedQuestions.length === 0 && (
                <tr>
                  <td colSpan="6" className="p-4 text-center text-gray-500">
                    Aucune question disponible.
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
          <div className="bg-white w-full max-w-2xl rounded-xl p-6 shadow-xl">
            <h3 className="text-xl font-semibold text-green-800 mb-4">
              {editingQuestion ? "Modifier la question" : "Ajouter une question"}
            </h3>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block font-medium mb-1">Code</label>
                <input
                  className="w-full border rounded-lg p-2"
                  value={form.question_code}
                  onChange={(e) => setForm({ ...form, question_code: e.target.value })}
                  placeholder="Q1"
                  disabled={loading}
                />
              </div>
              <div>
                <label className="block font-medium mb-1">Type de réponse</label>
                <select
                  className="w-full border rounded-lg p-2"
                  value={form.reponse_correcte ? "true" : "false"}
                  onChange={(e) =>
                    setForm({ ...form, reponse_correcte: e.target.value === "true" })
                  }
                  disabled={loading}
                >
                  <option value="true">Oui</option>
                  <option value="false">Non</option>
                </select>
              </div>
              <div className="md:col-span-2">
                <label className="block font-medium mb-1">Énoncé français</label>
                <textarea
                  className="w-full border rounded-lg p-2"
                  rows={3}
                  value={form.enonce_fr}
                  onChange={(e) => setForm({ ...form, enonce_fr: e.target.value })}
                  placeholder="Texte de la question..."
                  disabled={loading}
                />
              </div>
              <div className="md:col-span-2">
                <label className="block font-medium mb-1">Énoncé arabe</label>
                <textarea
                  className="w-full border rounded-lg p-2"
                  rows={3}
                  value={form.enonce_ar}
                  onChange={(e) => setForm({ ...form, enonce_ar: e.target.value })}
                  placeholder="Texte de la question..."
                  disabled={loading}
                />
              </div>
              <div className="md:col-span-2">
                <label className="block font-medium mb-1">Énoncé anglais</label>
                <textarea
                  className="w-full border rounded-lg p-2"
                  rows={3}
                  value={form.enonce_en}
                  onChange={(e) => setForm({ ...form, enonce_en: e.target.value })}
                  placeholder="Texte de la question..."
                  disabled={loading}
                />
              </div>
              <div>
                <label className="block font-medium mb-1">Image (optionnel)</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setForm({ ...form, image: e.target.files?.[0] || null })}
                  className="w-full border rounded-lg p-2"
                  disabled={loading}
                />
              </div>
              <div>
                <label className="block font-medium mb-1">Associer à une version</label>
                <select
                  className="w-full border rounded-lg p-2"
                  value={form.version_id}
                  onChange={(e) => setForm({ ...form, version_id: e.target.value })}
                  disabled={loading}
                >
                  <option value="">Aucune</option>
                  {versions.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.name || `Version ${v.version}`}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                className="px-4 py-2 rounded border hover:bg-gray-50"
                onClick={() => setShowModal(false)}
                disabled={loading}
              >
                Annuler
              </button>
              <button
                className="px-4 py-2 rounded bg-green-700 text-white hover:bg-green-800"
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