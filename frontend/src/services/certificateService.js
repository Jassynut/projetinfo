import api from "./api"

export const certificateService = {
  // Récupérer mes certificats
  getMyCertificates: async () => {
    const response = await api.get("/certificates/")
    return response.data
  },

  // Générer depuis une tentative
  generateFromAttempt: async (attemptId) => {
    const response = await api.post("/certificates/generate-from-attempt/", {
      attempt_id: attemptId,
    })
    return response.data
  },

  // Détails d'un certificat
  getCertificateDetails: async (certificateId) => {
    const response = await api.get(`/certificates/${certificateId}/`)
    return response.data
  },

  // Télécharger PDF
  downloadCertificate: async (certificateId) => {
    const response = await api.get(`/certificates/${certificateId}/download/`, {
      responseType: "blob",
    })
    return response.data
  },

  // Rechercher par nom/CIN
  searchCertificate: async (searchTerm) => {
    const response = await api.post("/certificates/search/", { search_term: searchTerm })
    return response.data
  },

  // Recherche publique
  searchCertificatePublic: async (searchTerm) => {
    const response = await api.post("/certificates/search-public/", { search_term: searchTerm })
    return response.data
  },
}
