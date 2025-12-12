import { useNavigate } from "react-router-dom";

export default function TopNav({ className = "" }) {
  const navigate = useNavigate();
  return (
    <div className={`flex justify-between items-center mb-6 ${className}`}>
      <button
        onClick={() => navigate(-1)}
        className="text-sm px-3 py-1 rounded border border-green-300 text-green-800 hover:bg-green-50"
      >
        ← Retour
      </button>
      <button
        onClick={() => navigate("/dashboard")}
        className="text-sm px-3 py-1 rounded border border-green-300 text-green-800 hover:bg-green-50"
      >
        Accueil
      </button>
    </div>
  );
}

