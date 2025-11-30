// frontend/src/components/Dashboard.js
import React from 'react';
import { Link } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
  const cartes = [
    {
      titre: '📋 Gestion des questionnaires',
      description: 'Créez et gérez vos tests Hygiéne Sécurité et Envirenement',
      lien: '/gestion',
      couleur: '#3498db'
    },
    {
      titre: '🎯 Commencer le test', 
      description: 'Passez un examen de certification',
      lien: '/tests',
      couleur: '#2ecc71'
    },
    {
      titre: '📄 Générer un certificat',
      description: 'Téléchargez vos attestations',
      lien: '/certificats',
      couleur: '#9b59b6'
    }
  ];

  return (
    <div className="dashboard-container">
      <h1>Tableau de bord HSE</h1>
      <p style={{textAlign: 'center', color: '#7f8c8d', marginBottom: '40px'}}>
        Bienvenue sur votre plateforme de formation et certification HSE
      </p>
      
      <div className="dashboard-grid">
        {cartes.map((carte, index) => (
          <div key={index} className="dashboard-card">
            <div className="card-icon">{carte.titre.split(' ')[0]}</div>
            <h3>{carte.titre}</h3>
            <p>{carte.description}</p>
            <Link 
              to={carte.lien} 
              className="card-button"
              style={{ backgroundColor: carte.couleur }}
            >
              Accéder
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
};

<<<<<<< HEAD
export default Dashboard;
=======
export default Dashboard;
>>>>>>> e6c3a406e42e952a97ca038274a784e7c63dc02d
