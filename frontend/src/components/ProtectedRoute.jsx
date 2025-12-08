import { Navigate, Outlet } from "react-router-dom"
import { useAuthStore } from "../store/authStore"

export default function ProtectedRoute({ requiredRole = null }) {
  const { user, token } = useAuthStore()

  if (!token) {
    return <Navigate to="/login" replace />
  }

  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
