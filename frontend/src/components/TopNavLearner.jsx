import { useNavigate } from "react-router-dom";

/**
 * Navigation limitée pour les apprenants (accès via QR code)
 * Ne contient pas de liens vers le dashboard ou les fonctionnalités admin
 */
export default function TopNavLearner({ className = "" }) {
  const navigate = useNavigate();
  
  return (
    <div className={`flex justify-between items-center mb-6 ${className}`}>
      <div className="flex items-center gap-2">
        <img src="/ocp-logo.png" alt="logo" className="w-8 h-8" />
        <span className="text-sm font-semibold text-green-800">Test HSE</span>
      </div>
      <div className="text-xs text-gray-600">
        Mode apprenant
      </div>
    </div>
  );
}

