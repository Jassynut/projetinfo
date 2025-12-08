"use client"

import Navbar from "../components/Navbar"
import Card from "../components/Card"
import { useNavigate } from "react-router-dom"
import { Users, BookOpen, BarChart3 } from "lucide-react"

export default function ManagerDashboard() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Tableau de bord Manager</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="cursor-pointer hover:shadow-lg transition" onClick={() => navigate("/manager/users")}>
            <div className="flex items-center gap-4">
              <Users className="text-blue-500" size={40} />
              <div>
                <p className="text-gray-600 text-sm">Gestion des utilisateurs</p>
                <p className="text-2xl font-bold">0</p>
              </div>
            </div>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition" onClick={() => navigate("/manager/tests")}>
            <div className="flex items-center gap-4">
              <BookOpen className="text-green-500" size={40} />
              <div>
                <p className="text-gray-600 text-sm">Gestion des tests</p>
                <p className="text-2xl font-bold">0</p>
              </div>
            </div>
          </Card>

          <Card className="hover:shadow-lg transition">
            <div className="flex items-center gap-4">
              <BarChart3 className="text-purple-500" size={40} />
              <div>
                <p className="text-gray-600 text-sm">Statistiques</p>
                <p className="text-2xl font-bold">0</p>
              </div>
            </div>
          </Card>
        </div>

        <Card title="Actions rapides">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => navigate("/manager/users")}
              className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
            >
              Gérer les utilisateurs
            </button>
            <button
              onClick={() => navigate("/manager/tests")}
              className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-semibold"
            >
              Gérer les tests
            </button>
          </div>
        </Card>
      </div>
    </div>
  )
}
