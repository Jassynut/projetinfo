import { create } from "zustand"
import { persist } from "zustand/middleware"

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      role: null,

      setUser: (userData, token) =>
        set({
          user: userData,
          token,
          role: userData.role || "user",
        }),

      logout: () =>
        set({
          user: null,
          token: null,
          role: null,
        }),

      isAuthenticated: () => get().token !== null,
    }),
    {
      name: "auth-store",
    },
  ),
)
