// Axios configuration with CSRF token handling
import axios from 'axios';
import { API_BASE } from '../config';
import { getCsrfToken, fetchCsrfToken } from './csrf';

// Create axios instance
const axiosInstance = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add CSRF token
axiosInstance.interceptors.request.use(
  async (config) => {
    // Only add CSRF token for state-changing methods (POST, PUT, PATCH, DELETE)
    if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase())) {
      let csrfToken = getCsrfToken();
      
      // If no token in cookies, try to fetch it
      if (!csrfToken) {
        try {
          csrfToken = await fetchCsrfToken(API_BASE);
        } catch (error) {
          console.warn('[Axios] Failed to fetch CSRF token:', error);
        }
      }
      
      // Add CSRF token to headers if available
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      } else {
        console.warn('[Axios] No CSRF token available for request:', config.url);
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    // If 403 and CSRF related, try to refresh token and retry
    if (error.response?.status === 403 && error.config && !error.config._retry) {
      const originalRequest = error.config;
      originalRequest._retry = true;
      
      // Try to get fresh CSRF token
      try {
        const csrfToken = await fetchCsrfToken(API_BASE);
        if (csrfToken) {
          originalRequest.headers['X-CSRFToken'] = csrfToken;
          return axiosInstance(originalRequest);
        }
      } catch (csrfError) {
        console.error('[Axios] Failed to refresh CSRF token:', csrfError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default axiosInstance;

