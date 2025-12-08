"use client"

import { useEffect, useState } from "react"
import Navbar from "../components/Navbar"
import Card from "../components/Card"
import LoadingSpinner from "../components/LoadingSpinner"
import { useAuthStore } from "../store/authStore"
import { hseUserService } from "../services/hseUserService"
import { certificateService } from "../services/certificateService"
import { Download } from "lucide-react"

export default function UserProfile() {
  const { user } = useAuthStore()
  const [userDetails, setUserDetails] = useState(null)
  const [certificates, setCertificates] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [userDetailsRes, certificatesRes] = await Promise.all([
          hseUserService.getUserDetails(user.id),
          certificateService.getMyCertificates(),
        ])
        setUserDetails(userDetailsRes)
        setCertificates(certificatesRes.results || certificatesRes)
      } catch (error) {
        console.error("Erreur:", error)
      } finally {
        setLoading(false)
      }
    }

    if (user?.id) {
      fetchData()
    }
  }, [user])

  const handleDownload = async (certificateId) => {
    try {
      const blob = await certificateService.downloadCertificate(certificateId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `certificate-${certificateId}.pdf`
      a.click()
    } catch (error) {
      alert("Erreur lors du téléchargement")
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Mon profil</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
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
              <div>
                <p className="text-sm text-gray-600">Département</p>
                <p className="text-lg">{userDetails?.department || "N/A"}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Date d'inscription</p>
                <p className="text-lg">{new Date(userDetails?.created_at).toLocaleDateString("fr-FR")}</p>
              </div>
            </div>
          </Card>

          <Card title="Statistiques">
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Tests passés</p>
                <p className="text-3xl font-bold text-blue-600">{userDetails?.test_count || 0}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Score moyen</p>
                <p className="text-3xl font-bold text-green-600">{userDetails?.average_score || 0}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Certificats obtenus</p>
                <p className="text-3xl font-bold text-purple-600">{certificates.length}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Présence</p>
                <p className={`text-lg font-semibold ${userDetails?.is_present ? "text-green-600" : "text-red-600"}`}>
                  {userDetails?.is_present ? "Présent" : "Absent"}
                </p>
              </div>
            </div>
          </Card>

          <Card title="Actions">
            <div className="space-y-3">
              <p className="text-sm text-gray-600">Accédez à vos certificats ci-dessous</p>
              <div className="space-y-2">
                {certificates.length > 0 ? (
                  certificates.map((cert) => (
                    <button
                      key={cert.id}
                      onClick={() => handleDownload(cert.id)}
                      className="w-full flex items-center justify-between px-3 py-2 bg-blue-50 hover:bg-blue-100 rounded-lg transition text-left"
                    >
                      <span className="text-sm font-medium text-gray-800">{cert.test_title}</span>
                      <Download size={16} className="text-blue-600" />
                    </button>
                  ))
                ) : (
                  <p className="text-gray-600 text-sm py-4">Aucun certificat disponible</p>
                )}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
