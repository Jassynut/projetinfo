"use client"

import { useState } from "react"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import Login from "./pages/Login"
import Dashboard from "./pages/Dashboard"
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
import "./App.css"

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const handleLogin = (email, password) => {
    // Mock authentication - replace with real API call
    if (email && password) {
      setIsAuthenticated(true)
    }
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
  }

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <Router>
      <div className="App">
        <Header onLogout={handleLogout} />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/gestion-questionnaires" element={<QuestionnairesList />} />
          <Route path="/editeur-questions" element={<QuestionEditor />} />
          <Route path="/gestion-versions" element={<VersionManagement />} />
          <Route path="/gestion-donnees" element={<ExcelDataManagement />} />
          <Route path="/certificats" element={<CertificateSearch />} />
          <Route path="/tableau-bord" element={<HSEDashboard />} />
          <Route path="/versions-test" element={<TestVersionsList />} />
          <Route path="/demarrer-test" element={<StartTest />} />
          <Route path="/test-version-selection" element={<TestVersionSelection />} />
          <Route path="/test-qr-code" element={<TestQRCode />} />
          <Route path="/test-taking" element={<TestTaking />} />
          <Route path="/test-success" element={<TestSuccess />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
