// Utility functions for CSRF token management

/**
 * Get CSRF token from cookies
 */
export const getCsrfToken = () => {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

/**
 * Fetch CSRF token from Django backend
 * Le cookie CSRF est automatiquement défini par le serveur avec @ensure_csrf_cookie
 */
export const fetchCsrfToken = async (apiBase) => {
  try {
    const response = await fetch(`${apiBase}/api/csrf-token/`, {
      method: 'GET',
      credentials: 'include', // IMPORTANT: pour recevoir le cookie
    });
    
    if (response.ok) {
      // Le cookie est automatiquement stocké par le navigateur
      // On peut maintenant le lire depuis les cookies
      const data = await response.json();
      // Essayer de récupérer depuis les cookies d'abord, sinon utiliser la réponse
      const tokenFromCookie = getCsrfToken();
      return tokenFromCookie || data.csrftoken || null;
    }
  } catch (error) {
    console.warn('[CSRF] Error fetching CSRF token:', error);
  }
  
  // Fallback to cookie
  return getCsrfToken();
};

/**
 * Ensure CSRF token is available
 * Tries to get it from cookies first, then from endpoint if needed
 */
export const ensureCsrfToken = async (apiBase) => {
  let token = getCsrfToken();
  
  if (!token) {
    token = await fetchCsrfToken(apiBase);
  }
  
  return token;
};

