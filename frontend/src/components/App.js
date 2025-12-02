"use client"

import { useState, useEffect } from "react"
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import axios from "axios"
import Login from "./pages/Login"
import stats from "./pages/stats"
import QuestionnairesList from "./pages/QuestionnairesList"
import QuestionEditor from "./pages/QuestionEditor"
import VersionManagement from "./pages/VersionManagement"
import ExcelDataManagement from "./pages/ExcelDataManagement"
import CertificateSearch from "./pages/CertificateSearch"
import HSEDashboard from "./pages/HSEDashboard"
import TestVersionsList from "./pages/TestVersionsList"
import Header from "./Header"
import StartTest from "./pages/StartTest"
import TestVersionSelection from "./pages/TestVersionSelection"
import TestQRCode from "./pages/TestQRCode"
import TestTaking from "./pages/TestTaking"
import TestSuccess from "./pages/TestSuccess"
import QrLogin from "./pages/QrLogin"  // ← NOUVELLE PAGE POUR LOGIN QR
import "./App.css"

// Configuration axios pour Django
axios.defaults.baseURL = "http://localhost:8000"
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = "csrftoken"
axios.defaults.xsrfHeaderName = "X-CSRFToken"

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [userData, setUserData] = useState(null)
  const [loading, setLoading] = useState(true)

  // Vérifier l'authentification au démarrage
  useEffect(() => {
    checkAuthentication()
  }, [])

  const checkAuthentication = async () => {
    try {
      const response = await axios.get("/api/auth/current-user/")
      if (response.data.success) {
        setIsAuthenticated(true)
        setUserData(response.data.user)
      }
    } catch (error) {
      console.log("Utilisateur non authentifié")
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async (email, password) => {
    try {
      // API Django pour l'authentification normale
      const response = await axios.post("/api/auth/login/", {
        username: email,
        password: password
      })
      
      if (response.data.success) {
        setIsAuthenticated(true)
        setUserData(response.data.user)
        return { success: true }
      }
    } catch (error) {
      console.error("Erreur login:", error)
      return { 
        success: false, 
        error: error.response?.data?.error || "Erreur d'authentification" 
      }
    }
  }

  const handleQrLogin = async (cin, testId) => {
    try {
      // API pour login via QR code
      const response = await axios.post(`/api/auth/test/${testId}/auth/`, {
        cin: cin
      })
      
      if (response.data.success) {
        setIsAuthenticated(true)
        setUserData(response.data.user)
        return { 
          success: true, 
          redirectTo: `/test-taking/${response.data.test_session?.id || testId}` 
        }
      }
    } catch (error) {
      console.error("Erreur QR login:", error)
      return { 
        success: false, 
        error: error.response?.data?.error || "CIN invalide" 
      }
    }
  }

  const handleLogout = async () => {
    try {
      await axios.post("/api/auth/logout/")
    } catch (error) {
      console.error("Erreur logout:", error)
    } finally {
      setIsAuthenticated(false)
      setUserData(null)
    }
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Chargement...</p>
      </div>
    )
  }

  // Routes publiques (accessibles sans auth)
  const publicRoutes = [
    "/qr-login/:testId",
    "/test-taking/:attemptId",
    "/test-success/:sessionId"
  ]

  // Si non authentifié et pas sur une route publique, rediriger vers login
  if (!isAuthenticated && !window.location.pathname.match(/^\/(qr-login|test-taking|test-success)/)) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <Router>
      <div className="App">
        {isAuthenticated && <Header onLogout={handleLogout} user={userData} />}
        
        <Routes>
          {/* Routes publiques */}
          <Route path="/qr-login/:testId" element={
            <QrLogin onQrLogin={handleQrLogin} />
          } />
          
          <Route path="/test-taking/:attemptId" element={
            isAuthenticated ? <TestTaking /> : <Navigate to="/" />
          } />
          
          <Route path="/test-success/:sessionId" element={
            isAuthenticated ? <TestSuccess /> : <Navigate to="/" />
          } />

          {/* Routes protégées */}
          <Route path="/" element={
            isAuthenticated ? <stats user={userData} /> : <Navigate to="/" />
          } />
          
          <Route path="/gestion-questionnaires" element={
            isAuthenticated ? <QuestionnairesList /> : <Navigate to="/" />
          } />
          
          <Route path="/editeur-questions" element={
            isAuthenticated ? <QuestionEditor /> : <Navigate to="/" />
          } />
          
          <Route path="/gestion-versions" element={
            isAuthenticated ? <VersionManagement /> : <Navigate to="/" />
          } />
          
          <Route path="/gestion-donnees" element={
            isAuthenticated ? <ExcelDataManagement /> : <Navigate to="/" />
          } />
          
          <Route path="/certificats" element={
            isAuthenticated ? <CertificateSearch /> : <Navigate to="/" />
          } />
          
          <Route path="/tableau-bord" element={
            isAuthenticated ? <HSEDashboard /> : <Navigate to="/" />
          } />
          
          <Route path="/versions-test" element={
            isAuthenticated ? <TestVersionsList /> : <Navigate to="/" />
          } />
          
          <Route path="/demarrer-test" element={
            isAuthenticated ? <StartTest /> : <Navigate to="/" />
          } />
          
          <Route path="/test-version-selection" element={
            isAuthenticated ? <TestVersionSelection /> : <Navigate to="/" />
          } />
          
          <Route path="/test-qr-code" element={
            isAuthenticated ? <TestQRCode /> : <Navigate to="/" />
          } />
        </Routes>
      </div>
    </Router>
  )
}

export default App