import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import TopNav from "../components/TopNav";
import { API_BASE } from "../config";

export default function ModifierVersion() {
  const { versionId } = useParams();
  const navigate = useNavigate();
  const [version, setVersion] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [allQuestions, setAllQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedQuestionId, setSelectedQuestionId] = useState("");
  const [draggedIndex, setDraggedIndex] = useState(null);

  useEffect(() => {
    if (versionId) {
      fetchVersion();
      fetchAllQuestions();
    }
  }, [versionId]);

  const fetchVersion = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_BASE}/api/versions/${versionId}`);
      const versionData = res.data?.version || res.data;
      setVersion(versionData);
      
      // Récupérer les questions de la version dans l'ordre
      if (versionData.id) {
        // Si ordre_questions est disponible, l'utiliser pour ordonner
        if (versionData.ordre_questions && versionData.ordre_questions.length > 0) {
          // Récupérer toutes les questions
          const allQuestionsRes = await axios.get(`${API_BASE}/api/questions/`);
          const allQuestionsList = allQuestionsRes.data?.questions || allQuestionsRes.data || [];
          
          // Ordonner selon ordre_questions de la base de données
          const orderedQuestionsList = [];
          for (const qid of versionData.ordre_questions) {
            const question = allQuestionsList.find(q => q.id === qid);
            if (question) {
              orderedQuestionsList.push(question);
            }
          }
          setQuestions(orderedQuestionsList);
        } else if (versionData.questions && versionData.questions.length > 0) {
          // Si les questions sont déjà dans la réponse, les utiliser
          // Mais s'assurer qu'on a aussi l'ordre
          setQuestions(versionData.questions);
          // Si ordre_questions n'est pas défini mais qu'on a des questions, le créer
          if (!versionData.ordre_questions && versionData.questions.length > 0) {
            const orderFromQuestions = versionData.questions.map(q => q.id);
            setVersion({ ...versionData, ordre_questions: orderFromQuestions });
          }
        } else {
          // Fallback : utiliser l'endpoint questions
          const questionsRes = await axios.get(`${API_BASE}/api/versions/${versionData.id}/questions`);
          const questionsList = questionsRes.data?.questions || [];
          setQuestions(questionsList);
          // Créer l'ordre à partir des questions récupérées
          if (questionsList.length > 0 && !versionData.ordre_questions) {
            const orderFromQuestions = questionsList.map(q => q.id);
            setVersion({ ...versionData, ordre_questions: orderFromQuestions });
          }
        }
      }
    } catch (err) {
      console.error("Erreur chargement version:", err);
      setError("Impossible de charger la version.");
    } finally {
      setLoading(false);
    }
  };

  const fetchAllQuestions = async () => {
    try {
      // Récupérer toutes les questions (gérer la pagination si nécessaire)
      let allQuestionsList = [];
      let url = `${API_BASE}/api/questions/`;
      let hasMore = true;
      let page = 1;
      
      while (hasMore) {
        try {
          const res = await axios.get(url, {
            params: page > 1 ? { page } : {}
          });
          
          // Gérer différents formats de réponse
          let questionsList = [];
          if (res.data?.results) {
            // Format paginé
            questionsList = res.data.results;
            hasMore = !!res.data.next;
            page++;
          } else if (res.data?.questions) {
            // Format avec clé 'questions'
            questionsList = res.data.questions;
            hasMore = false;
          } else if (Array.isArray(res.data)) {
            // Format array direct
            questionsList = res.data;
            hasMore = false;
          } else {
            hasMore = false;
          }
          
          allQuestionsList = [...allQuestionsList, ...questionsList];
        } catch (err) {
          console.error("Erreur lors de la récupération des questions:", err);
          hasMore = false;
        }
      }
      
      // Trier les questions par question_code (Q1, Q2, Q3, etc.)
      const sortedQuestions = [...allQuestionsList].sort((a, b) => {
        const codeA = a.question_code || '';
        const codeB = b.question_code || '';
        // Extraire les numéros des codes (Q1 -> 1, Q2 -> 2, etc.)
        const numA = parseInt(codeA.replace(/\D/g, '')) || 0;
        const numB = parseInt(codeB.replace(/\D/g, '')) || 0;
        return numA - numB;
      });
      
      console.log(`Total questions chargées: ${sortedQuestions.length}`);
      // Log des premières questions pour vérifier les IDs
      if (sortedQuestions.length > 0) {
        console.log(`[DEBUG] Exemple de questions chargées:`, sortedQuestions.slice(0, 5).map(q => ({
          id: q.id,
          question_code: q.question_code,
          type_id: typeof q.id
        })));
      }
      setAllQuestions(sortedQuestions);
    } catch (err) {
      console.error("Erreur chargement questions:", err);
      setError("Impossible de charger toutes les questions.");
    }
  };

  const handleDeleteQuestion = async (questionId) => {
    if (!confirm("Supprimer cette question de la version ?")) return;
    
    try {
      const currentOrder = version?.ordre_questions || [];
      const newOrder = currentOrder.filter(id => id !== questionId);
      
      // Sauvegarder immédiatement dans la base de données
      const response = await axios.patch(`${API_BASE}/api/versions/${versionId}/update-order/`, {
        ordre_questions: newOrder
      });
      
      // Mettre à jour l'état avec la réponse du serveur
      const confirmedOrder = response.data?.ordre_questions || newOrder;
      
      setQuestions(questions.filter(q => q.id !== questionId));
      setVersion({ ...version, ordre_questions: confirmedOrder });
    } catch (err) {
      console.error("Erreur suppression:", err);
      alert("Erreur lors de la suppression de la question.");
    }
  };

  const handleAddQuestion = async () => {
    if (!selectedQuestionId) {
      alert("Veuillez sélectionner une question.");
      return;
    }

    try {
      // Convertir l'ID sélectionné en nombre (s'assurer que c'est bien un nombre)
      const questionIdInt = parseInt(selectedQuestionId, 10);
      
      if (isNaN(questionIdInt)) {
        alert("ID de question invalide.");
        return;
      }
      
      // Trouver la question dans allQuestions pour vérifier qu'elle existe
      const selectedQuestion = allQuestions.find(q => {
        const qId = typeof q.id === 'string' ? parseInt(q.id, 10) : q.id;
        return qId === questionIdInt;
      });
      
      if (!selectedQuestion) {
        alert("Question non trouvée dans la liste.");
        return;
      }
      
      // S'assurer que version.ordre_questions est initialisé et normaliser les IDs (tous en nombres)
      const currentOrder = (version?.ordre_questions || []).map(id => 
        typeof id === 'string' ? parseInt(id, 10) : id
      );
      
      // Vérifier si la question est déjà dans la version (comparaison stricte)
      if (currentOrder.includes(questionIdInt)) {
        alert("Cette question est déjà dans la version.");
        return;
      }

      const newOrder = [...currentOrder, questionIdInt];
      
      console.log(`[DEBUG] Question sélectionnée:`, selectedQuestion);
      console.log(`[DEBUG] ID sélectionné (string):`, selectedQuestionId);
      console.log(`[DEBUG] ID sélectionné (int):`, questionIdInt);
      console.log(`[DEBUG] Question code:`, selectedQuestion.question_code);
      console.log(`[DEBUG] Nouvel ordre à envoyer:`, newOrder);
      
      // Sauvegarder immédiatement dans la base de données
      const response = await axios.patch(`${API_BASE}/api/versions/${versionId}/update-order/`, {
        ordre_questions: newOrder
      });
      
      console.log(`[DEBUG] Réponse serveur:`, response.data);

      // Mettre à jour l'état avec la réponse du serveur pour garantir la synchronisation
      const confirmedOrder = response.data?.ordre_questions || newOrder;
      
      // Récupérer la question ajoutée avec l'ID correct
      const addedQuestion = allQuestions.find(q => {
        const qId = typeof q.id === 'string' ? parseInt(q.id, 10) : q.id;
        return qId === questionIdInt;
      });
      
      if (addedQuestion) {
        setQuestions([...questions, addedQuestion]);
      }
      
      // Mettre à jour l'état de la version avec l'ordre confirmé
      setVersion({ ...version, ordre_questions: confirmedOrder });
      setSelectedQuestionId("");
    } catch (err) {
      console.error("Erreur ajout:", err);
      console.error("Détails:", err.response?.data);
      const errorMsg = err.response?.data?.error || err.message || "Erreur de connexion au serveur";
      const fullError = err.code === 'ERR_NETWORK' || err.code === 'ERR_CONNECTION_REFUSED'
        ? `Impossible de se connecter au serveur. Vérifiez que le backend est accessible à ${API_BASE}`
        : errorMsg;
      alert(`Erreur lors de l'ajout de la question: ${fullError}`);
    }
  };

  const handleDragStart = (e, index) => {
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/html", e.target);
    e.target.style.opacity = "0.5";
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  };

  const handleDragEnd = (e) => {
    e.target.style.opacity = "";
    setDraggedIndex(null);
  };

  const handleDrop = async (e, dropIndex) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === dropIndex) return;

    // S'assurer que version.ordre_questions est initialisé
    const currentOrder = version?.ordre_questions || [];
    const newOrder = [...currentOrder];
    const draggedItem = newOrder[draggedIndex];
    newOrder.splice(draggedIndex, 1);
    newOrder.splice(dropIndex, 0, draggedItem);

    // Mettre à jour l'état local immédiatement pour feedback visuel
    const reorderedQuestions = [...questions];
    const draggedQuestion = reorderedQuestions[draggedIndex];
    reorderedQuestions.splice(draggedIndex, 1);
    reorderedQuestions.splice(dropIndex, 0, draggedQuestion);
    setQuestions(reorderedQuestions);
    setVersion({ ...version, ordre_questions: newOrder });

    // Sauvegarder immédiatement sur le serveur
    try {
      const response = await axios.patch(`${API_BASE}/api/versions/${versionId}/update-order/`, {
        ordre_questions: newOrder
      });
      
      // Mettre à jour avec l'ordre confirmé par le serveur
      const confirmedOrder = response.data?.ordre_questions || newOrder;
      setVersion({ ...version, ordre_questions: confirmedOrder });
    } catch (err) {
      console.error("Erreur sauvegarde ordre:", err);
      alert("Erreur lors de la sauvegarde de l'ordre. Veuillez réessayer.");
      // Recharger en cas d'erreur pour restaurer l'état correct
      fetchVersion();
      return;
    }

    setDraggedIndex(null);
  };

  const handleSave = async () => {
    setLoading(true);
    setError("");
    try {
      await axios.patch(`${API_BASE}/api/versions/${versionId}/update-order/`, {
        ordre_questions: version.ordre_questions
      });
      alert("Ordre des questions enregistré avec succès !");
      navigate("/gerer-versions");
    } catch (err) {
      console.error("Erreur sauvegarde:", err);
      setError("Erreur lors de la sauvegarde.");
    } finally {
      setLoading(false);
    }
  };

  // Filtrer les questions disponibles (non déjà dans la version) et les trier par question_code
  const availableQuestions = allQuestions
    .filter(q => {
      const currentOrder = (version?.ordre_questions || []).map(id => 
        typeof id === 'string' ? parseInt(id, 10) : id
      );
      // Normaliser l'ID de la question pour la comparaison
      const qId = typeof q.id === 'string' ? parseInt(q.id, 10) : q.id;
      return !currentOrder.includes(qId);
    })
    .sort((a, b) => {
      // Trier par question_code (Q1, Q2, Q3, etc.)
      const codeA = a.question_code || '';
      const codeB = b.question_code || '';
      // Extraire les numéros des codes (Q1 -> 1, Q2 -> 2, etc.)
      const numA = parseInt(codeA.replace(/\D/g, '')) || 0;
      const numB = parseInt(codeB.replace(/\D/g, '')) || 0;
      return numA - numB;
    });

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-8">
      <TopNav className="mb-4" />
      
      <div className="flex items-center mb-6">
        <h1 className="text-3xl font-bold text-green-900">
          Modifier {version?.name || `Version ${version?.version || ""}`}
        </h1>
      </div>

      <div className="bg-white rounded-xl shadow-lg border border-green-200 p-6">
        {error && <p className="text-red-600 mb-4">{error}</p>}
        {loading && <p className="text-gray-600 mb-4">Chargement...</p>}

        {/* Liste des questions */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-green-800 mb-4">Questions de la version</h2>
          {questions.length === 0 ? (
            <p className="text-gray-500">Aucune question dans cette version.</p>
          ) : (
            <div className="space-y-2">
              {questions.map((question, index) => (
                <div
                  key={question.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, index)}
                  onDragOver={handleDragOver}
                  onDrop={(e) => handleDrop(e, index)}
                  onDragEnd={handleDragEnd}
                  className={`flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200 cursor-move transition-all ${
                    draggedIndex === index ? "opacity-50 bg-green-100" : "hover:bg-green-100"
                  }`}
                >
                  <div className="flex items-center gap-3 flex-1">
                    <span className="font-semibold text-green-700 w-8">⋮⋮</span>
                    <span className="font-semibold text-green-700 w-8">{index + 1}.</span>
                    <span className="flex-1">
                      {question.question_code || `Q${index + 1}`}: {question.enonce_fr || question.text || "Question sans texte"}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleDeleteQuestion(question.id)}
                      className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      Supprimer
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Ajouter une question */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-green-800 mb-3">Ajouter une question existante :</h3>
          <div className="flex gap-3">
            <select
              value={selectedQuestionId}
              onChange={(e) => setSelectedQuestionId(e.target.value)}
              className="flex-1 border rounded-lg p-2"
            >
              <option value="">-- Sélectionner une question --</option>
              {availableQuestions.length === 0 ? (
                <option value="" disabled>
                  Aucune question disponible (toutes les questions sont déjà dans cette version)
                </option>
              ) : (
                availableQuestions.map((q) => {
                  // S'assurer que l'ID est bien un nombre pour la valeur
                  const questionId = typeof q.id === 'string' ? parseInt(q.id, 10) : q.id;
                  return (
                    <option key={q.id} value={questionId}>
                      {q.question_code || `Q${q.id}`}: {q.enonce_fr || q.text || "Question sans texte"}
                    </option>
                  );
                })
              )}
            </select>
            <button
              onClick={handleAddQuestion}
              className="bg-green-700 text-white px-4 py-2 rounded-lg hover:bg-green-800"
            >
              Ajouter
            </button>
          </div>
        </div>

        {/* Boutons d'action */}
        <div className="flex justify-end gap-3">
          <button
            onClick={() => navigate("/gerer-versions")}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Annuler
          </button>
          <button
            onClick={handleSave}
            disabled={loading}
            className="px-6 py-2 bg-green-700 text-white rounded-lg hover:bg-green-800 disabled:opacity-50 flex items-center gap-2"
          >
            <span>💾</span> Enregistrer
          </button>
        </div>
      </div>

      <footer className="text-center mt-20 text-gray-600 text-sm">
        © 2025 OCP – Portail Interne HSE. Tous droits réservés.
      </footer>
    </div>
  );
}

