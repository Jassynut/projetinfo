import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { useAuthStore } from "./store/authStore"
import ProtectedRoute from "./components/ProtectedRoute"

// Pages
import Login from "./pages/Login"
import Dashboard from "./pages/Dashboard"
import UserProfile from "./pages/UserProfile"
import TestList from "./pages/TestList"
import TestInterface from "./pages/TestInterface"
import TestResults from "./pages/TestResults"
import CertificateSearch from "./pages/CertificateSearch"
import ManagerDashboard from "./pages/ManagerDashboard"
import UserManagement from "./pages/UserManagement"
import TestManagement from "./pages/TestManagement"

export default function App() {
  const { user } = useAuthStore()

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/certificate-search" element={<CertificateSearch />} />

        {/* Protected Routes - User */}
        <Route element={<ProtectedRoute requiredRole="user" />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/profile" element={<UserProfile />} />
          <Route path="/tests" element={<TestList />} />
          <Route path="/test/:testId" element={<TestInterface />} />
          <Route path="/results/:attemptId" element={<TestResults />} />
        </Route>

        {/* Protected Routes - Manager */}
        <Route element={<ProtectedRoute requiredRole="manager" />}>
          <Route path="/manager" element={<ManagerDashboard />} />
          <Route path="/manager/users" element={<UserManagement />} />
          <Route path="/manager/tests" element={<TestManagement />} />
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}
