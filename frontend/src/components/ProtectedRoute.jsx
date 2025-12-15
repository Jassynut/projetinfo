import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

/**
 * Composant pour protéger les routes admin contre l'accès des apprenants
 */
export function ProtectedRoute({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  
  useEffect(() => {
    // Vérifier si l'utilisateur est un apprenant (accès via QR code)
    const isLearner = sessionStorage.getItem("isLearner") === "true";
    const isManager = localStorage.getItem("loggedIn") === "true" && localStorage.getItem("userType") === "manager";
    
    // Si c'est un manager, supprimer le flag apprenant
    if (isManager) {
      sessionStorage.removeItem("isLearner");
      sessionStorage.removeItem("currentTestId");
      return; // Les managers ont accès à tout
    }
    
    if (isLearner) {
      // Routes interdites aux apprenants
      const adminRoutes = [
        "/dashboard",
        "/database",
        "/hse-dashboard",
        "/gestion-questionnaires",
        "/gerer-versions",
        "/modifier-version",
        "/gerer-questions",
        "/gerer-admins",
        "/test/selection",
        "/test/commencer"
      ];
      
      // Si l'apprenant essaie d'accéder à une route admin, rediriger
      if (adminRoutes.some(route => location.pathname.startsWith(route))) {
        // Récupérer l'ID du test depuis sessionStorage ou rediriger vers une page d'erreur
        const testId = sessionStorage.getItem("currentTestId");
        if (testId) {
          navigate(`/test/${testId}/passer`, { replace: true });
        } else {
          // Si pas de test ID, rediriger vers la page de login
          navigate("/", { replace: true });
        }
      }
    }
  }, [location.pathname, navigate]);
  
  return children;
}

