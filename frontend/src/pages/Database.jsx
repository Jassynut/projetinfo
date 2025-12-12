import { useState } from "react";
import axios from "axios";
import TopNav from "../components/TopNav";

export default function Database() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [tableData, setTableData] = useState([]);

  const triggerFileDialog = () => {
    document.getElementById("excelInput").click();
  };

  const handleFileSelected = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Veuillez sélectionner un fichier Excel.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/stats/upload_excel/",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      console.log("Réponse Django :", res.data);

      if (res.data.success) {
        setTableData(res.data.data);
      } else {
        alert("Réponse backend : " + JSON.stringify(res.data, null, 2));
        console.log("🔥 Réponse complète du backend :", res.data);
      }
    } catch (err) {
      console.error(err);
      alert("Erreur lors de l'import.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-10">
      <TopNav className="mb-4" />

      {/* Header */}
      <div className="flex justify-between items-center mb-10">
        <div className="flex items-center gap-3">
          <img src="/ocp-logo.png" alt="logo" className="w-12" />
          <h1 className="text-xl font-bold text-green-900">
            Induction HSE - Jorf Lasfar
          </h1>
        </div>

        <a href="/dashboard" className="text-green-700 font-semibold hover:underline">
          Accueil
        </a>
      </div>

      {/* TITRE */}
      <h2 className="text-3xl font-bold text-gray-800 mb-2">Fichiers Excel</h2>
      <p className="text-gray-600 mb-6">Choisissez la date et la table à consulter.</p>

      {/* Onglet */}
      <div className="border-b border-green-300 mb-8">
        <button className="pb-2 border-b-4 border-green-600 text-green-700 font-semibold">
          Données des Agents
        </button>
      </div>

      {/* Champs date */}
      <div className="flex items-center gap-3 mb-10">
        <input className="w-20 p-2 border rounded-lg" placeholder="JJ" />
        <input className="w-20 p-2 border rounded-lg" placeholder="MM" />
        <input className="w-24 p-2 border rounded-lg" placeholder="AAAA" />
        <button className="bg-green-700 text-white px-4 py-2 rounded-lg">
          Voir
        </button>
      </div>

      {/* BLOC TABLE + BOUTON */}
      <div className="bg-white p-6 rounded-xl shadow-lg border border-green-200">

        <div className="flex justify-between items-center mb-6">
          <h3 className="text-green-700 text-xl font-semibold">Table des données</h3>

          {/* BOUTON IMPORT */}
          <button
            onClick={triggerFileDialog}
            className="bg-green-700 text-white px-4 py-2 rounded-lg"
          >
            + Importer fichier Excel
          </button>

          {/* INPUT FICHIER */}
          <input
            id="excelInput"
            type="file"
            accept=".xlsx, .xls"
            className="hidden"
            onChange={handleFileSelected}
          />
        </div>

        {/* AFFICHAGE DU NOM + BOUTON IMPORTER */}
        {selectedFile && (
          <div className="mb-6">
            <p className="text-gray-700 mb-2">
              Fichier sélectionné : <strong>{selectedFile.name}</strong>
            </p>

            <button
              onClick={handleUpload}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow hover:bg-blue-700 transition"
            >
              Importer
            </button>
          </div>
        )}

        {/* TABLEAU DYNAMIQUE */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">

            <thead>
              {tableData.length > 0 && (
                <tr className="bg-green-50 text-green-700 font-semibold">
                  {Object.keys(tableData[0]).map((col, idx) => (
                    <th key={idx} className="p-3 border">{col}</th>
                  ))}
                </tr>
              )}
            </thead>

            <tbody>
              {tableData.length > 0 &&
                tableData.map((row, i) => (
                  <tr key={i}>
                    {Object.values(row).map((value, j) => (
                      <td key={j} className="border p-2">{value}</td>
                    ))}
                  </tr>
                ))}
            </tbody>

          </table>

          {tableData.length === 0 && (
            <p className="text-gray-500 italic">Aucune donnée importée.</p>
          )}
        </div>

      </div>

      {/* FOOTER */}
      <footer className="text-center mt-20 text-gray-600 text-sm">
        © 2025 OCP – Portail Interne HSE. Tous droits réservés.
      </footer>
    </div>
  );
}
