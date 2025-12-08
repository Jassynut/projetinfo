"use client"

import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import Navbar from "../components/Navbar"
import Card from "../components/Card"
import LoadingSpinner from "../components/LoadingSpinner"
import { testService } from "../services/testService"
import { certificateService } from "../services/certificateService"
import { CheckCircle, XCircle, Download } from "lucide-react"

export default function TestResults() {
  const { attemptId } = useParams()
  const navigate = useNavigate()
  const [attempt, setAttempt] = useState(null)
  const [loading, setLoading] = useState(true)
  const [certificateGenerated, setCertificateGenerated] = useState(false)

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await testService.getAttemptDetails(attemptId)
        setAttempt(data)
      } catch (error) {
        console.error("Erreur:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchResults()
  }, [attemptId])

  const handleGenerateCertificate = async () => {
    try {
      const certificate = await certificateService.generateFromAttempt(attemptId)
      setCertificateGenerated(true)
      alert("Certificat généré avec succès!")
    } catch (error) {
      alert("Erreur lors de la génération du certificat")
    }
  }

  const handleDownloadCertificate = async () => {
    try {
      const blob = await certificateService.downloadCertificate(attempt.certificate_id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `certificate-${attempt.certificate_id}.pdf`
      a.click()
    } catch (error) {
      alert("Erreur lors du téléchargement")
    }
  }

  if (loading) return <LoadingSpinner />

  const passed = attempt?.score >= 60

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 py-8">
        <Card className="text-center mb-8">
          <div className="flex justify-center mb-6">
            {passed ? (
              <CheckCircle className="text-green-500" size={80} />
            ) : (
              <XCircle className="text-red-500" size={80} />
            )}
          </div>

          <h1 className={`text-4xl font-bold mb-2 ${passed ? "text-green-600" : "text-red-600"}`}>
            {passed ? "Test réussi!" : "Test échoué"}
          </h1>

          <div className="text-6xl font-bold text-blue-600 my-4">{attempt?.score}%</div>

          <p className="text-gray-600 text-lg mb-8">
            Score: {attempt?.score_numerator}/{attempt?.score_denominator}
          </p>

          {passed && !certificateGenerated && (
            <button
              onClick={handleGenerateCertificate}
              className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-semibold"
            >
              Générer un certificat
            </button>
          )}

          {certificateGenerated && attempt?.certificate_id && (
            <button
              onClick={handleDownloadCertificate}
              className="flex items-center justify-center gap-2 px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold mx-auto"
            >
              <Download size={20} />
              Télécharger le certificat
            </button>
          )}
        </Card>

        <Card title="Détails des réponses">
          <div className="space-y-4">
            {attempt?.detailed_results?.map((result, index) => (
              <div key={index} className={`p-4 rounded-lg ${result.is_correct ? "bg-green-50" : "bg-red-50"}`}>
                <div className="flex items-start gap-3">
                  {result.is_correct ? (
                    <CheckCircle className="text-green-600 flex-shrink-0 mt-1" size={20} />
                  ) : (
                    <XCircle className="text-red-600 flex-shrink-0 mt-1" size={20} />
                  )}
                  <div className="flex-1">
                    <p className="font-semibold text-gray-800 mb-2">
                      Q{index + 1}: {result.question}
                    </p>
                    <p className="text-sm text-gray-700 mb-2">Votre réponse: {result.user_answer}</p>
                    {!result.is_correct && (
                      <p className="text-sm text-green-700">Réponse correcte: {result.correct_answer}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <div className="mt-8 text-center">
          <button
            onClick={() => navigate("/tests")}
            className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition font-semibold"
          >
            Revenir aux tests
          </button>
        </div>
      </div>
    </div>
  )
}
