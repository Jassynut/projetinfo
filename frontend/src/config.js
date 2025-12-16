// Configuration de l'API
// Utilise l'IP locale pour Docker ou localhost pour le développement local
const getApiBase = () => {
  // Vérifier si on est en production (Docker) ou développement
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Utiliser l'IP locale pour Docker, sinon localhost
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://127.0.0.1:8000';
  }
  
  // Pour Docker, utiliser le même hostname que le frontend
  // Cela permet de fonctionner avec localhost ou avec une IP locale
  const port = window.location.port || '3000';
  const protocol = window.location.protocol;
  // Extraire le hostname et utiliser le port 8000 pour le backend
  return `${protocol}//${hostname}:8000`;
};

export const API_BASE = getApiBase();

