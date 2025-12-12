import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Database from "./pages/Database";
import DashboardHSE from "./pages/DashboardHSE";
import GestionQuestionnaires from "./pages/GestionQuestionnaires";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/database" element={<Database />} />
        <Route path="/hse-dashboard" element={<DashboardHSE />} />
        <Route path="/gestion-questionnaires" element={<GestionQuestionnaires />} />
      </Routes>
    </BrowserRouter>
  );
}
