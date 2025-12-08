"use client"

import { useEffect, useState } from "react"
import { useParams, useSearchParams, useNavigate } from "react-router-dom"
import Navbar from "../components/Navbar"
import Card from "../components/Card"
import LoadingSpinner from "../components/LoadingSpinner"
import { testService } from "../services/testService"
import { Clock, ChevronLeft, ChevronRight } from "lucide-react"

export default function TestInterface() {
  const { testId } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const attemptId = searchParams.get("attemptId")

  const [test, setTest] = useState(null)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [timeLeft, setTimeLeft] = useState(null)

  useEffect(() => {
    const fetchTest = async () => {
      try {
        const data = await testService.getTestDetails(testId)
        setTest(data)
        setTimeLeft(data.duration * 60)
      } catch (error) {
        console.error("Erreur:", error)
        alert("Erreur lors du chargement du test")
      } finally {
        setLoading(false)
      }
    }

    fetchTest()
  }, [testId])

  useEffect(() => {
    if (!timeLeft) return

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          handleSubmit()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [timeLeft])

  const handleSelectAnswer = (questionId, answerIndex) => {
    setAnswers({
      ...answers,
      [questionId]: answerIndex,
    })
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const response = await testService.submitAttempt(attemptId, answers)
      navigate(`/results/${attemptId}`)
    } catch (error) {
      alert("Erreur lors de la soumission")
      setSubmitting(false)
    }
  }

  if (loading) return <LoadingSpinner />

  if (!test || !test.questions || test.questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <Card className="text-center py-12">
            <p className="text-gray-600">Erreur: Aucune question trouvée</p>
          </Card>
        </div>
      </div>
    )
  }

  const currentQuestion = test.questions[currentQuestionIndex]
  const progress = ((currentQuestionIndex + 1) / test.questions.length) * 100

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">{test.title}</h1>
          <div className="flex items-center gap-2 text-lg font-semibold text-red-600">
            <Clock size={24} />
            <span>
              {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, "0")}
            </span>
          </div>
        </div>

        <div className="mb-6">
          <div className="flex justify-between text-sm mb-2">
            <span>
              Question {currentQuestionIndex + 1} / {test.questions.length}
            </span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${progress}%` }}></div>
          </div>
        </div>

        <Card>
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">{currentQuestion.text}</h2>

            <div className="space-y-3">
              {currentQuestion.choices.map((choice, index) => (
                <button
                  key={index}
                  onClick={() => handleSelectAnswer(currentQuestion.id, index)}
                  className={`w-full p-4 rounded-lg border-2 transition text-left ${
                    answers[currentQuestion.id] === index
                      ? "border-blue-600 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300 bg-white"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        answers[currentQuestion.id] === index ? "border-blue-600 bg-blue-600" : "border-gray-300"
                      }`}
                    >
                      {answers[currentQuestion.id] === index && <div className="w-2 h-2 bg-white rounded-full"></div>}
                    </div>
                    <span className="text-gray-700">{choice}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-between gap-4">
            <button
              onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
              disabled={currentQuestionIndex === 0}
              className="flex items-center gap-2 px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition disabled:opacity-50"
            >
              <ChevronLeft size={20} />
              Précédent
            </button>

            {currentQuestionIndex === test.questions.length - 1 ? (
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="flex-1 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 font-semibold"
              >
                {submitting ? "Soumission..." : "Terminer le test"}
              </button>
            ) : (
              <button
                onClick={() => setCurrentQuestionIndex(currentQuestionIndex + 1)}
                className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Suivant
                <ChevronRight size={20} />
              </button>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
