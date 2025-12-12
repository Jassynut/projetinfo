import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Database from "./pages/Database";
import DashboardHSE from "./pages/DashboardHSE";
import GestionQuestionnaires from "./pages/GestionQuestionnaires";
import GestionVersions from "./pages/GestionVersions";
import GestionQuestions from "./pages/GestionQuestions";
import ConsultationCertificats from "./pages/ConsultationCertificats";
import SelectionTest from "./pages/SelectionTest";
import CommencerTest from "./pages/CommencerTest";
import PasserTest from "./pages/PasserTest";
import ResultatTest from "./pages/ResultatTest";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/database" element={<Database />} />
        <Route path="/hse-dashboard" element={<DashboardHSE />} />
        <Route path="/gestion-questionnaires" element={<GestionQuestionnaires />} />
        <Route path="/gerer-versions" element={<GestionVersions />} />
        <Route path="/gerer-questions" element={<GestionQuestions />} />
        <Route path="/certificats" element={<ConsultationCertificats />} />
        <Route path="/test/selection" element={<SelectionTest />} />
        <Route path="/test/commencer" element={<CommencerTest />} />
        <Route path="/test/:id/passer" element={<PasserTest />} />
        <Route path="/test/:id/resultat" element={<ResultatTest />} />
      </Routes>
    </BrowserRouter>
  );
}
