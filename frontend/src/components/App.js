// frontend/src/components/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './Dashboard';

function App() {
  return (
    <Router>
      <div className="App">
        {/* Navigation simple */}
        <nav style={{ padding: '20px', background: '#f8f9fa', borderBottom: '1px solid #dee2e6' }}>
          <h2 style={{ margin: 0 }}>🏥 Plateforme HSE</h2>
        </nav>
        
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/gestion" element={<div style={{padding: '40px'}}>Page Gestion des questionnaires (à créer)</div>} />
          <Route path="/tests" element={<div style={{padding: '40px'}}>Page Tests (à créer)</div>} />
          <Route path="/certificats" element={<div style={{padding: '40px'}}>Page Certificats (à créer)</div>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;