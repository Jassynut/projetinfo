import api from "./api"

export const authService = {
  login: async (username, password) => {
    const response = await api.post("/auth/login/", { username, password })
    return response.data
  },

  logout: async () => {
    try {
      await api.post("/auth/logout/")
    } catch (error) {
      console.error("Logout error:", error)
    }
  },

  getCurrentUser: async () => {
    const response = await api.get("/auth/me/")
    return response.data
  },
}
