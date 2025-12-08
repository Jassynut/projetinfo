"use client"

import { useEffect, useState } from "react"
import Navbar from "../components/Navbar"
import Card from "../components/Card"
import LoadingSpinner from "../components/LoadingSpinner"
import { testService } from "../services/testService"
import { Plus, Edit2, Trash2 } from "lucide-react"

export default function TestManagement() {
  const [tests, setTests] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)

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

  if (loading) return <LoadingSpinner />

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Gestion des tests</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
          >
            <Plus size={20} />
            Créer un test
          </button>
        </div>

        {showForm && (
          <Card title="Créer un nouveau test" className="mb-8">
            <p className="text-gray-600">Formulaire de création de test - À implémenter</p>
          </Card>
        )}

        <Card>
          <div className="grid gap-4">
            {tests.map((test) => (
              <div key={test.id} className="p-4 border rounded-lg hover:shadow-lg transition">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-800 mb-2">{test.title}</h3>
                    <p className="text-gray-600 text-sm mb-2">{test.description}</p>
                    <p className="text-sm text-gray-500">
                      {test.question_count} questions • {test.duration} min
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button className="p-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition">
                      <Edit2 size={18} />
                    </button>
                    <button className="p-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition">
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
