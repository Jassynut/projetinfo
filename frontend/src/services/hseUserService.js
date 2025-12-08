import api from "./api"

export const hseUserService = {
  // Récupérer tous les utilisateurs
  getAllUsers: async (filters = {}) => {
    const response = await api.get("/hse/users/", { params: filters })
    return response.data
  },

  // Récupérer les détails d'un utilisateur
  getUserDetails: async (userId) => {
    const response = await api.get(`/hse/users/${userId}/`)
    return response.data
  },

  // Rechercher par CIN
  searchByCin: async (cin) => {
    const response = await api.get("/hse/users/search-by-cin/", { params: { cin } })
    return response.data
  },

  // Mettre à jour la présence
  updatePresence: async (userId, isPresent) => {
    const response = await api.patch(`/hse/users/${userId}/update-presence/`, {
      is_present: isPresent,
    })
    return response.data
  },

  // Historique des tests d'un utilisateur
  getTestHistory: async (userId) => {
    const response = await api.get(`/hse/users/${userId}/test-history/`)
    return response.data
  },

  // Statistiques
  getStatistics: async () => {
    const response = await api.get("/hse/users/statistics/")
    return response.data
  },
}
