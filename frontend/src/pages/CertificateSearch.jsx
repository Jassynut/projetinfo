"use client"

import { useState } from "react"
import { certificateService } from "../services/certificateService"
import Card from "../components/Card"
import { Search, Download } from "lucide-react"
import { useNavigate } from "react-router-dom"

export default function CertificateSearch() {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState("")
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchTerm.trim()) return

    setLoading(true)
    setSearched(true)

    try {
      const data = await certificateService.searchCertificatePublic(searchTerm)
      setResults(data.results || data)
    } catch (error) {
      console.error("Erreur:", error)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button onClick={() => navigate("/login")} className="text-blue-600 hover:text-blue-700 font-semibold">
            Se connecter
          </button>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 py-12">
        <Card className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Rechercher un certificat</h1>
          <p className="text-gray-600 mb-6">Entrez le nom ou le CIN pour trouver un certificat</p>

          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Nom complet ou CIN..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 font-semibold"
            >
              <Search size={20} />
              Rechercher
            </button>
          </form>
        </Card>

        {searched && (
          <>
            {loading ? (
              <Card className="text-center py-12">
                <p className="text-gray-600">Recherche en cours...</p>
              </Card>
            ) : results.length > 0 ? (
              <div className="grid gap-6">
                {results.map((certificate) => (
                  <Card key={certificate.id} className="hover:shadow-lg transition">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-800 mb-2">{certificate.user_name}</h3>
                        <p className="text-gray-600 mb-1">CIN: {certificate.user_cin}</p>
                        <p className="text-gray-600 mb-1">Test: {certificate.test_title}</p>
                        <p className="text-gray-600">
                          Date: {new Date(certificate.created_at).toLocaleDateString("fr-FR")}
                        </p>
                      </div>
                      <button
                        onClick={() => handleDownload(certificate.id)}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                      >
                        <Download size={18} />
                        Télécharger
                      </button>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <Card className="text-center py-12">
                <p className="text-gray-600">Aucun certificat trouvé pour cette recherche</p>
              </Card>
            )}
          </>
        )}
      </div>
    </div>
  )
}
