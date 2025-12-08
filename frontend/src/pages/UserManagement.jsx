"use client"

import { useEffect, useState } from "react"
import Navbar from "../components/Navbar"
import Card from "../components/Card"
import LoadingSpinner from "../components/LoadingSpinner"
import { hseUserService } from "../services/hseUserService"
import { Search, CheckCircle } from "lucide-react"

export default function UserManagement() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedUser, setSelectedUser] = useState(null)

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await hseUserService.getAllUsers()
        setUsers(data.results || data)
      } catch (error) {
        console.error("Erreur:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchUsers()
  }, [])

  const handleTogglePresence = async (userId, currentStatus) => {
    try {
      await hseUserService.updatePresence(userId, !currentStatus)
      setUsers(users.map((u) => (u.id === userId ? { ...u, is_present: !currentStatus } : u)))
    } catch (error) {
      alert("Erreur lors de la mise à jour")
    }
  }

  const filteredUsers = users.filter(
    (user) =>
      user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.cin.includes(searchTerm),
  )

  if (loading) return <LoadingSpinner />

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Gestion des utilisateurs</h1>

        <Card className="mb-8">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Rechercher par nom, email ou CIN..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </Card>

        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Nom</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Email</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">CIN</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Présence</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Score</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-gray-50 transition">
                    <td className="py-3 px-4 text-gray-800">{user.full_name}</td>
                    <td className="py-3 px-4 text-gray-600">{user.email}</td>
                    <td className="py-3 px-4 text-gray-600 font-mono">{user.cin}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          user.is_present ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                        }`}
                      >
                        {user.is_present ? "Présent" : "Absent"}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-800 font-semibold">{user.score}/21</td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => handleTogglePresence(user.id, user.is_present)}
                        className="flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition text-sm"
                      >
                        <CheckCircle size={16} />
                        Modifier présence
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredUsers.length === 0 && <p className="text-center text-gray-600 py-8">Aucun utilisateur trouvé</p>}
        </Card>
      </div>
    </div>
  )
}
