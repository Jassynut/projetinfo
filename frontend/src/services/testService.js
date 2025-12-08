import api from "./api"

export const testService = {
  // Lister les tests
  getAllTests: async (filters = {}) => {
    const response = await api.get("/tests/", { params: filters })
    return response.data
  },

  // Détails d'un test
  getTestDetails: async (testId) => {
    const response = await api.get(`/tests/${testId}/`)
    return response.data
  },

  // Démarrer une tentative
  startAttempt: async (testId) => {
    const response = await api.post("/tests/attempts/start/", { test_id: testId })
    return response.data
  },

  // Soumettre les réponses
  submitAttempt: async (attemptId, answers) => {
    const response = await api.post(`/tests/attempts/${attemptId}/submit/`, { answers })
    return response.data
  },

  // Récupérer mes tentatives
  getMyAttempts: async () => {
    const response = await api.get("/tests/my-attempts/")
    return response.data
  },

  // Détails d'une tentative
  getAttemptDetails: async (attemptId) => {
    const response = await api.get(`/tests/attempts/${attemptId}/`)
    return response.data
  },
}
