import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import axios from "axios";
import TopNavLearner from "../components/TopNavLearner";
import { API_BASE } from "../config";
const TEST_DURATION_SECONDS = 600; // 10 minutes
const CNI_REGEX = /^[A-Z]{1,2}\d{5,6}$/i;

export default function PasserTest() {
  const { id } = useParams(); // test id or version
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  // Tous les useState d'abord
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [current, setCurrent] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [secondsLeft, setSecondsLeft] = useState(TEST_DURATION_SECONDS);
  const [submitting, setSubmitting] = useState(false);
  const [needsCin, setNeedsCin] = useState(false);
  const [cinInput, setCinInput] = useState("");
  const [accessGranted, setAccessGranted] = useState(false); // État pour l'accès autorisé
  const [needsLanguage, setNeedsLanguage] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("fr");
  const [cin, setCin] = useState("");

  // Log pour déboguer
  useEffect(() => {
    console.log("PasserTest - ID récupéré depuis les paramètres:", id);
    console.log("PasserTest - URL complète:", window.location.href);
    console.log("PasserTest - Search params:", searchParams.toString());
    if (!id) {
      console.error("PasserTest - ERREUR: ID manquant dans les paramètres de route");
      setError("ID du test manquant dans l'URL. Veuillez scanner le QR code à nouveau ou contacter l'administrateur.");
    } else {
      console.log("PasserTest - Page chargée avec succès, ID:", id);
    }
  }, [id, searchParams]);

  const total = questions.length;
  const currentQuestion = questions[current];

  // Countdown démarre uniquement après autorisation d'accès (accessGranted = true)
  useEffect(() => {
    if (!accessGranted || needsCin) return;
    const timer = setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          clearInterval(timer);
          handleSubmit(); // auto-submit
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [accessGranted, needsCin]);

  // Marquer l'utilisateur comme apprenant (accès limité) et stocker l'ID du test
  useEffect(() => {
    sessionStorage.setItem("isLearner", "true");
    if (id) {
      sessionStorage.setItem("currentTestId", id);
    }
  }, [id]);

  // Fetch questions on mount
  useEffect(() => {
    // Vérifier que l'ID du test est valide
    if (!id) {
      setError("ID du test manquant. Veuillez sélectionner une version de test.");
      return;
    }
    
    const cniParam = searchParams.get("cni");
    const stored = cniParam || sessionStorage.getItem("cni");
    if (stored && CNI_REGEX.test(stored)) {
      sessionStorage.setItem("cni", stored.toUpperCase());
      verifyCinAndGrantAccess(stored.toUpperCase());
    } else {
      setNeedsCin(true);
    }
  }, [id, searchParams]);

  const verifyCinAndGrantAccess = async (cinValue) => {
    setLoading(true);
    setError("");
    
    try {
      // Vérifier que le CIN existe dans la table HSEUser
      const response = await axios.get(`${API_BASE}/api/hse/users/search/`, {
        params: { cin: cinValue.toUpperCase() }
      });

      if (response.data.success && response.data.user) {
        // CIN trouvé dans HSEUser → accès autorisé
        setCin(cinValue.toUpperCase());
        sessionStorage.setItem("cni", cinValue.toUpperCase());
        setNeedsCin(false);
        setNeedsLanguage(true);
      } else {
        setError("CIN non trouvé dans la base de données. Vérifiez votre numéro.");
      }
    } catch (err) {
      console.error("Erreur vérification CIN:", err);
      setError(
        err.response?.data?.error || 
        "CIN non trouvé dans la base de données. Vérifiez votre numéro."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleCinSubmit = async () => {
    const value = cinInput.trim().toUpperCase();
    if (!CNI_REGEX.test(value)) {
      setError("Format CNI invalide (ex: AE112456)");
      return;
    }
    await verifyCinAndGrantAccess(value);
  };

  const handleLanguageSelect = (lang) => {
    setSelectedLanguage(lang);
    setNeedsLanguage(false);
    setAccessGranted(true);
    setSecondsLeft(TEST_DURATION_SECONDS);
    fetchQuestions(lang);
  };

  const fetchQuestions = async (lang = "fr") => {
    if (!id) {
      setError("ID du test manquant. Veuillez sélectionner une version de test.");
      return;
    }
    
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_BASE}/api/test/${id}/questions`);
      const items = res.data?.questions || res.data || [];
      if (items.length === 0) {
        setError("Aucune question trouvée pour ce test.");
      } else {
        setQuestions(items);
      }
    } catch (err) {
      console.error("Erreur chargement questions:", err);
      const errorMsg = err.response?.data?.error || err.response?.data?.detail || "Impossible de charger les questions.";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const progress = useMemo(() => {
    if (total === 0) return 0;
    const answered = Object.keys(answers).length;
    return Math.round((answered / total) * 100);
  }, [answers, total]);

  // Fonction pour obtenir le texte des boutons selon la langue
  const getAnswerButtonText = (isYes) => {
    if (selectedLanguage === "ar") {
      return isYes ? "نعم" : "لا";
    } else if (selectedLanguage === "en") {
      return isYes ? "Yes" : "No";
    } else {
      return isYes ? "Oui" : "Non";
    }
  };

  // Vérifier si toutes les questions sont répondues
  const allQuestionsAnswered = useMemo(() => {
    return total > 0 && Object.keys(answers).length === total;
  }, [answers, total]);

  const formatTime = (s) => {
    const m = Math.floor(s / 60)
      .toString()
      .padStart(2, "0");
    const sec = (s % 60).toString().padStart(2, "0");
    return `${m}:${sec}`;
  };

  const handleAnswer = async (value) => {
    if (!currentQuestion) return;
    const questionId = currentQuestion.id;
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
    try {
      await axios.post(`${API_BASE}/api/test/${id}/reponse`, {
        question_id: questionId,
        answer: value,
      }, {
        withCredentials: true
      });
    } catch (err) {
      // silencieux, l'enregistrement final gèrera
    }
  };

  const handleNext = () => {
    setCurrent((c) => Math.min(c + 1, total - 1));
  };

  const handlePrev = () => {
    setCurrent((c) => Math.max(c - 1, 0));
  };

  const handleSubmit = async () => {
    if (submitting) return;
    if (total > 0 && Object.keys(answers).length < total) {
      setError("Merci de répondre à toutes les questions avant de terminer.");
      return;
    }
    
    // Récupérer le CIN depuis l'état ou sessionStorage
    const currentCin = cin || sessionStorage.getItem("cni") || "";
    if (!currentCin) {
      setError("CIN non trouvé. Veuillez recommencer le test.");
      return;
    }
    
    setSubmitting(true);
    setError("");
    try {
      // Récupérer l'état du test depuis localStorage (pour les managers)
      const testEtat = localStorage.getItem('selectedTestEtat') || 'test_final';
      
      const response = await axios.post(`${API_BASE}/api/test/${id}/terminer`, {
        answers,
        time_taken_seconds: TEST_DURATION_SECONDS - secondsLeft,
        cin: currentCin.toUpperCase(),
        langue: selectedLanguage,
        etat: testEtat,
      }, {
        withCredentials: true
      });
      
      // Stocker les données du résultat dans sessionStorage pour la page de résultat
      if (response.data?.success) {
        sessionStorage.setItem('testResult', JSON.stringify({
          ...response.data,
          cin: currentCin.toUpperCase()
        }));
        navigate(`/test/${id}/resultat`);
      } else {
        setError(response.data?.error || "Erreur lors de l'enregistrement du test.");
      }
    } catch (err) {
      console.error("Erreur soumission test:", err);
      const errorMsg = err.response?.data?.error || err.response?.data?.message || "Erreur lors de la soumission du test.";
      setError(errorMsg);
    } finally {
      setSubmitting(false);
    }
  };

  // Vérifier que l'ID est présent
  if (!id) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-4 md:p-8">
        <div className="max-w-5xl mx-auto bg-white rounded-xl shadow-lg border border-green-200 p-6">
          <TopNavLearner className="mb-4" />
          <div className="text-center py-8">
            <h1 className="text-xl font-bold text-red-600 mb-4">Erreur</h1>
            <p className="text-gray-700 mb-4">
              ID du test manquant. Veuillez sélectionner une version de test depuis la page de sélection.
            </p>
            <button
              onClick={() => {
                // Pour les apprenants, on ne peut pas retourner à la sélection
                // On reste sur la page de test
                window.location.reload();
              }}
              className="bg-green-700 text-white px-6 py-3 rounded-lg shadow hover:bg-green-800"
            >
              Recharger la page
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-4 md:p-8">
      <div className="max-w-5xl mx-auto bg-white rounded-xl shadow-lg border border-green-200 p-6">
        <TopNavLearner className="mb-4" />
        <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-xl font-bold text-green-900">Test HSE</h1>
            <p className="text-sm text-gray-600">
              Temps restant :{" "}
              <span className="font-semibold text-green-700">
                {formatTime(secondsLeft)}
              </span>
            </p>
          </div>
          <div className="w-full md:w-1/2">
            <div className="text-sm text-gray-600 mb-1">
              Progression : {Math.min(progress, 100)}% (
              {Object.keys(answers).length}/{total})
            </div>
            <div className="w-full h-3 bg-gray-200 rounded-full">
              <div
                className="h-3 bg-green-600 rounded-full transition-all"
                style={{ width: `${Math.min(progress, 100)}%` }}
              />
            </div>
          </div>
        </header>

        {error && <p className="text-red-600 mb-4">{error}</p>}
        {needsCin && (
          <div className="space-y-3 mb-6">
            <p className="text-sm text-gray-700">
              Merci de saisir votre CNI pour démarrer le test.
            </p>
            <input
              className="w-full border rounded-lg p-3"
              placeholder="AE112456"
              value={cinInput}
              onChange={(e) => setCinInput(e.target.value)}
            />
            <button
              className="w-full bg-green-700 text-white py-3 rounded-lg shadow hover:bg-green-800"
              onClick={handleCinSubmit}
            >
              Continuer
            </button>
          </div>
        )}
        {needsLanguage && (
          <div className="space-y-3 mb-6">
            <p className="text-sm text-gray-700 font-semibold">
              Veuillez choisir votre langue préférée / Please choose your preferred language / يرجى اختيار لغتك المفضلة
            </p>
            <div className="grid grid-cols-3 gap-3">
              <button
                className="p-4 border-2 rounded-lg hover:bg-green-50 transition-all"
                onClick={() => handleLanguageSelect("fr")}
              >
                <div className="text-lg font-semibold">Français</div>
              </button>
              <button
                className="p-4 border-2 rounded-lg hover:bg-green-50 transition-all"
                onClick={() => handleLanguageSelect("en")}
              >
                <div className="text-lg font-semibold">English</div>
              </button>
              <button
                className="p-4 border-2 rounded-lg hover:bg-green-50 transition-all"
                onClick={() => handleLanguageSelect("ar")}
              >
                <div className="text-lg font-semibold">العربية</div>
              </button>
            </div>
          </div>
        )}
        {loading && <p className="text-gray-600">Chargement des questions...</p>}

        {!loading && currentQuestion && (
          <div className="space-y-4">
            <div className="text-sm text-gray-600">
              {currentQuestion?.question_code || `Question ${current + 1}`} / {total}
            </div>
            <div className="border rounded-xl p-4 shadow-sm bg-green-50">
              {currentQuestion.image_url && (
                <img
                  src={currentQuestion.image_url.startsWith('http') 
                    ? currentQuestion.image_url 
                    : `${API_BASE}${currentQuestion.image_url.startsWith('/') ? '' : '/'}${currentQuestion.image_url}`}
                  alt="illustration"
                  className="w-full max-h-64 object-contain rounded mb-4"
                  onError={(e) => {
                    console.error("Erreur chargement image:", currentQuestion.image_url);
                    e.target.style.display = 'none';
                  }}
                />
              )}
              <p className="text-lg font-semibold text-green-900">
                {selectedLanguage === "fr" && (currentQuestion.enonce_fr || currentQuestion.get_enonce?.("fr"))}
                {selectedLanguage === "ar" && (currentQuestion.enonce_ar || currentQuestion.get_enonce?.("ar") || currentQuestion.enonce_fr)}
                {selectedLanguage === "en" && (currentQuestion.enonce_en || currentQuestion.get_enonce?.("en") || currentQuestion.enonce_fr)}
              </p>
            </div>

            <div className="flex gap-3">
              <button
                className={`flex-1 py-3 rounded-lg border ${
                  answers[currentQuestion.id] === true
                    ? "bg-green-700 text-white"
                    : "bg-white text-green-800"
                }`}
                onClick={() => handleAnswer(true)}
              >
                {getAnswerButtonText(true)}
              </button>
              <button
                className={`flex-1 py-3 rounded-lg border ${
                  answers[currentQuestion.id] === false
                    ? "bg-red-600 text-white"
                    : "bg-white text-green-800"
                }`}
                onClick={() => handleAnswer(false)}
              >
                {getAnswerButtonText(false)}
              </button>
            </div>

            <div className="flex justify-between mt-4">
              <button
                className="px-4 py-2 rounded-lg border"
                onClick={handlePrev}
                disabled={current === 0}
              >
                {selectedLanguage === "ar" ? "السابق" : selectedLanguage === "en" ? "Previous" : "Précédent"}
              </button>
              <div className="flex gap-3">
                <button
                  className="px-4 py-2 rounded-lg border"
                  onClick={handleNext}
                  disabled={current >= total - 1}
                >
                  {selectedLanguage === "ar" ? "التالي" : selectedLanguage === "en" ? "Next" : "Suivant"}
                </button>
                {/* Afficher le bouton "Terminer le test" uniquement si toutes les questions sont répondues */}
                {allQuestionsAnswered && (
                  <button
                    className="px-4 py-2 rounded-lg bg-green-700 text-white"
                    onClick={handleSubmit}
                    disabled={submitting}
                  >
                    {selectedLanguage === "ar" ? "إنهاء الاختبار" : selectedLanguage === "en" ? "Finish test" : "Terminer le test"}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {!loading && !currentQuestion && (
          <p className="text-gray-600">Aucune question trouvée pour ce test.</p>
        )}
      </div>
    </div>
  );
}