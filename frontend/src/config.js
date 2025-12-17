// Configuration de l'API
// Utilise le proxy nginx qui redirige vers le backend
const getApiBase = () => {
  const hostname = window.location.hostname;
  const port = window.location.port || '';
  const protocol = window.location.protocol || 'http:';
  
  // Utiliser le même hostname et port que le frontend
  // Le proxy nginx redirigera automatiquement /api/* vers le backend
  // et les routes comme /manager/login/ aussi
  const baseUrl = `${protocol}//${hostname}${port ? ':' + port : ''}`;
  
  // Pour les routes /api/*, retourner juste le base URL car nginx proxy gère /api/
  // Pour les autres routes (comme /manager/login/), elles seront aussi proxifiées
  return baseUrl;
};

export const API_BASE = getApiBase();

