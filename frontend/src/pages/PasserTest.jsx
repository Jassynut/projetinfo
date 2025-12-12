import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import axios from "axios";
import TopNav from "../components/TopNav";

const API_BASE = "http://127.0.0.1:8000";
const TEST_DURATION_SECONDS = 600; // 10 minutes
const CNI_REGEX = /^[A-Z]{1,2}\d{5,6}$/i;

export default function PasserTest() {
  const { id } = useParams(); // test id or version
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [current, setCurrent] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [secondsLeft, setSecondsLeft] = useState(TEST_DURATION_SECONDS);
  const [submitting, setSubmitting] = useState(false);
  const [needsCin, setNeedsCin] = useState(false);
  const [cinInput, setCinInput] = useState("");

  const total = questions.length;
  const currentQuestion = questions[current];

  // Countdown démarre uniquement après saisie/validation du CNI
  useEffect(() => {
    if (needsCin) return;
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
  }, [needsCin]);

  // Fetch questions on mount
  useEffect(() => {
    const cniParam = searchParams.get("cni");
    const stored = cniParam || sessionStorage.getItem("cni");
    if (stored && CNI_REGEX.test(stored)) {
      sessionStorage.setItem("cni", stored.toUpperCase());
      setSecondsLeft(TEST_DURATION_SECONDS);
      fetchQuestions();
      setNeedsCin(false);
    } else {
      setNeedsCin(true);
    }
  }, [id, searchParams]);

  const handleCinSubmit = async () => {
    const value = cinInput.trim().toUpperCase();
    if (!CNI_REGEX.test(value)) {
      setError("Format CNI invalide (ex: AE112456)");
      return;
    }
    setError("");
    try {
      await axios.post(`${API_BASE}/api/test/verifier-cni`, { cni: value });
    } catch (err) {
      // on autorise quand même le passage si l'API n'est pas dispo
    }
    sessionStorage.setItem("cni", value);
    setNeedsCin(false);
    setSecondsLeft(TEST_DURATION_SECONDS);
    fetchQuestions();
  };

  const fetchQuestions = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_BASE}/api/test/${id}/questions`);
      const items = res.data?.questions || res.data || [];
      setQuestions(items);
    } catch (err) {
      setError("Impossible de charger les questions.");
    } finally {
      setLoading(false);
    }
  };

  const progress = useMemo(() => {
    if (total === 0) return 0;
    const answered = Object.keys(answers).length;
    return Math.round((answered / total) * 100);
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
    setSubmitting(true);
    setError("");
    try {
      await axios.post(`${API_BASE}/api/test/${id}/terminer`, {
        answers,
        time_taken_seconds: TEST_DURATION_SECONDS - secondsLeft,
      });
      navigate(`/test/${id}/resultat`);
    } catch (err) {
      setError("Erreur lors de la soumission du test.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-4 md:p-8">
      <div className="max-w-5xl mx-auto bg-white rounded-xl shadow-lg border border-green-200 p-6">
        <TopNav className="mb-4" />
        <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-xl font-bold text-green-900">Test HSE</h1>
            <p className="text-sm text-gray-600">
              Temps restant : <span className="font-semibold text-green-700">{formatTime(secondsLeft)}</span>
            </p>
          </div>
          <div className="w-full md:w-1/2">
            <div className="text-sm text-gray-600 mb-1">
              Progression : {Math.min(progress, 100)}% ({Object.keys(answers).length}/{total})
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
        {loading && <p className="text-gray-600">Chargement des questions...</p>}

        {!loading && currentQuestion && (
          <div className="space-y-4">
            <div className="text-sm text-gray-600">
              Question {current + 1} / {total}
            </div>
            <div className="border rounded-xl p-4 shadow-sm bg-green-50">
              {currentQuestion.image_url && (
                <img
                  src={currentQuestion.image_url}
                  alt="illustration"
                  className="w-full max-h-64 object-contain rounded mb-4"
                />
              )}
              <p className="text-lg font-semibold text-green-900">{currentQuestion.enonce_fr || currentQuestion.enonce}</p>
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
                Oui
              </button>
              <button
                className={`flex-1 py-3 rounded-lg border ${
                  answers[currentQuestion.id] === false
                    ? "bg-red-600 text-white"
                    : "bg-white text-green-800"
                }`}
                onClick={() => handleAnswer(false)}
              >
                Non
              </button>
            </div>

            <div className="flex justify-between mt-4">
              <button
                className="px-4 py-2 rounded-lg border"
                onClick={handlePrev}
                disabled={current === 0}
              >
                Précédent
              </button>
              <div className="flex gap-3">
                <button
                  className="px-4 py-2 rounded-lg border"
                  onClick={handleNext}
                  disabled={current >= total - 1}
                >
                  Suivant
                </button>
                <button
                  className="px-4 py-2 rounded-lg bg-green-700 text-white"
                  onClick={handleSubmit}
                  disabled={submitting}
                >
                  Terminer le test
                </button>
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

