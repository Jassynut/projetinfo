import { useNavigate } from "react-router-dom";

export default function TopNav({ className = "" }) {
  const navigate = useNavigate();
  return (
    <div className={`flex justify-between items-center mb-6 ${className}`}>
      <button
        id="back-button"
        name="back"
        type="button"
        onClick={() => navigate(-1)}
        className="text-sm px-3 py-1 rounded border border-green-300 text-green-800 hover:bg-green-50"
      >
        ← Retour
      </button>
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
        <button
          id="home-button"
          name="home"
          type="button"
          onClick={() => navigate("/dashboard")}
          className="text-sm px-3 py-1 rounded border border-green-300 text-green-800 hover:bg-green-50"
        >
          Accueil
        </button>
      </div>
    </div>
  );
}

