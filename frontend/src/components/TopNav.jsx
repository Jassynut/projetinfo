import { useNavigate, useLocation } from "react-router-dom";

export default function TopNav({ className = "" }) {
  const navigate = useNavigate();
  const location = useLocation();
  
  const currentPath = location.pathname;
  const isDashboard = currentPath === "/dashboard";
  
  // Déterminer la destination du bouton "Retour"
  const getBackDestination = () => {
    // Pour la page gestion-questionnaires, toujours retourner au dashboard pour éviter les boucles
    if (currentPath === "/gestion-questionnaires") {
      return "/dashboard";
    }
    
    // Pour les autres pages, on ne peut pas savoir à l'avance où navigate(-1) mènera
    // On retourne null pour indiquer qu'on utilisera navigate(-1)
    return null;
  };
  
  const handleBack = () => {
    const backDest = getBackDestination();
    if (backDest) {
      navigate(backDest);
    } else {
      navigate(-1);
    }
  };
  
  // Vérifier si "Retour" et "Accueil" mènent vers la même page
  // Si on est sur gestion-questionnaires, "Retour" va vers dashboard, donc même destination que "Accueil"
  const backDest = getBackDestination();
  const homeDest = "/dashboard";
  const backGoesToHome = backDest === homeDest;
  
  // Afficher "Accueil" seulement si :
  // 1. On n'est pas sur le dashboard
  // 2. Le bouton "Retour" ne mène pas déjà au dashboard (sinon on n'affiche que "Retour")
  const showHomeButton = !isDashboard && !backGoesToHome;
  
  return (
    <div className={`flex justify-between items-center mb-6 ${className}`}>
      {!isDashboard && (
        <button
          id="back-button"
          name="back"
          type="button"
          onClick={handleBack}
          className="text-sm px-3 py-1 rounded border border-green-300 text-green-800 hover:bg-green-50"
        >
          ← Retour
        </button>
      )}
      <div className="flex gap-2 items-center">
        <button
          id="manage-admins-button"
          name="manage-admins"
          type="button"
          onClick={() => navigate("/gerer-admins")}
          className="text-sm px-4 py-2 rounded-lg border-2 border-blue-400 bg-blue-100 text-blue-900 hover:bg-blue-200 font-bold shadow-sm transition-all"
          title="Gérer les admins/managers"
        >
          👥 Gérer les admins
        </button>
        {showHomeButton && (
          <button
            id="home-button"
            name="home"
            type="button"
            onClick={() => navigate("/dashboard")}
            className="text-sm px-3 py-1 rounded border border-green-300 text-green-800 hover:bg-green-50"
          >
            Accueil
          </button>
        )}
      </div>
    </div>
  );
}

