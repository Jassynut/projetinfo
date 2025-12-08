"use client"

import { useEffect, useState } from "react"
import Navbar from "../components/Navbar"
import Card from "../components/Card"
import LoadingSpinner from "../components/LoadingSpinner"
import { testService } from "../services/testService"
import { useNavigate } from "react-router-dom"
import { Play, Clock, CheckCircle } from "lucide-react"

export default function TestList() {
  const navigate = useNavigate()
  const [tests, setTests] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchTests = async () => {
      try {
        const data = await testService.getAllTests()
        setTests(data.results || data)
      } catch (error) {
        console.error("Erreur:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchTests()
  }, [])

  const handleStartTest = async (testId) => {
    try {
      const attempt = await testService.startAttempt(testId)
      navigate(`/test/${testId}?attemptId=${attempt.id}`)
    } catch (error) {
      alert("Erreur lors du démarrage du test")
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Tests disponibles</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tests.map((test) => (
            <Card key={test.id} className="hover:shadow-lg transition cursor-pointer">
              <h3 className="text-xl font-bold text-gray-800 mb-2">{test.title}</h3>
              <p className="text-gray-600 text-sm mb-4">{test.description}</p>

              <div className="space-y-2 mb-6">
                <div className="flex items-center gap-2 text-gray-700">
                  <Clock size={18} className="text-blue-500" />
                  <span>{test.duration || 30} minutes</span>
                </div>
                <div className="flex items-center gap-2 text-gray-700">
                  <CheckCircle size={18} className="text-green-500" />
                  <span>{test.question_count || 0} questions</span>
                </div>
              </div>

              <button
                onClick={() => handleStartTest(test.id)}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
              >
                <Play size={18} />
                Commencer
              </button>
            </Card>
          ))}
        </div>

        {tests.length === 0 && (
          <Card className="text-center py-12">
            <p className="text-gray-600">Aucun test disponible pour le moment</p>
          </Card>
        )}
      </div>
    </div>
  )
}
