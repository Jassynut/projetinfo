"use client"

import { useEffect, useState } from "react"
import Navbar from "../components/Navbar"
import Card from "../components/Card"
import LoadingSpinner from "../components/LoadingSpinner"
import { useAuthStore } from "../store/authStore"
import { hseUserService } from "../services/hseUserService"
import { useNavigate } from "react-router-dom"
import { BookOpen, Award, CheckCircle, Clock } from "lucide-react"

export default function Dashboard() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [userDetails, setUserDetails] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUserDetails = async () => {
      try {
        const data = await hseUserService.getUserDetails(user.id)
        setUserDetails(data)
      } catch (error) {
        console.error("Erreur lors du chargement des détails:", error)
      } finally {
        setLoading(false)
      }
    }

    if (user?.id) {
      fetchUserDetails()
    }
  }, [user])

  if (loading) return <LoadingSpinner />

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Tableau de bord</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="border-l-4 border-blue-500">
            <div className="flex items-center gap-4">
              <BookOpen className="text-blue-500" size={32} />
              <div>
                <p className="text-gray-600 text-sm">Tests passés</p>
                <p className="text-2xl font-bold">{userDetails?.test_count || 0}</p>
              </div>
            </div>
          </Card>

          <Card className="border-l-4 border-green-500">
            <div className="flex items-center gap-4">
              <Award className="text-green-500" size={32} />
              <div>
                <p className="text-gray-600 text-sm">Score moyen</p>
                <p className="text-2xl font-bold">{userDetails?.average_score || 0}%</p>
              </div>
            </div>
          </Card>

          <Card className="border-l-4 border-yellow-500">
            <div className="flex items-center gap-4">
              <CheckCircle className="text-yellow-500" size={32} />
              <div>
                <p className="text-gray-600 text-sm">Certificats</p>
                <p className="text-2xl font-bold">{userDetails?.certificate_count || 0}</p>
              </div>
            </div>
          </Card>

          <Card className="border-l-4 border-purple-500">
            <div className="flex items-center gap-4">
              <Clock className="text-purple-500" size={32} />
              <div>
                <p className="text-gray-600 text-sm">Présence</p>
                <p className="text-2xl font-bold">{userDetails?.is_present ? "Oui" : "Non"}</p>
              </div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card title="Informations personnelles">
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Nom complet</p>
                <p className="text-lg font-semibold">{userDetails?.full_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="text-lg">{userDetails?.email}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">CIN</p>
                <p className="text-lg font-mono">{userDetails?.cin}</p>
              </div>
              <button
                onClick={() => navigate("/profile")}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Voir le profil
              </button>
            </div>
          </Card>

          <Card title="Actions rapides">
            <div className="space-y-3">
              <button
                onClick={() => navigate("/tests")}
                className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:shadow-lg transition font-semibold"
              >
                Passer un test
              </button>
              <button
                onClick={() => navigate("/profile")}
                className="w-full px-4 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition font-semibold"
              >
                Voir mes certificats
              </button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
