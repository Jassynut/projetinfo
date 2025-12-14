import { useState, useEffect } from "react";
import axios from "axios";
import TopNav from "../components/TopNav";

const API_BASE = "http://127.0.0.1:8000";

export default function Database() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [presenceMap, setPresenceMap] = useState({}); // Map pour stocker la présence par CIN ou ID
  const [filterDate, setFilterDate] = useState(''); // Date pour filtrer les utilisateurs
  const [selectedUsers, setSelectedUsers] = useState([]); // IDs des utilisateurs sélectionnés pour suppression

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async (dateFilter = null) => {
    setLoading(true);
    try {
      // Construire l'URL avec le filtre de date si fourni et page_size pour récupérer tous les utilisateurs
      let url = `${API_BASE}/api/hse/users/list/`;
      const params = new URLSearchParams();
      params.append('page_size', '10000'); // Nombre très élevé pour récupérer tous les utilisateurs
      if (dateFilter) {
        params.append('date_ajout', dateFilter);
      }
      url += `?${params.toString()}`;
      
      // Utiliser l'endpoint simple qui retourne le bon format
      const res = await axios.get(url);
      if (res.data && res.data.success && res.data.users) {
        setUsers(res.data.users);
        // Initialiser la map de présence avec les données de la base
        const presence = {};
        res.data.users.forEach(user => {
          const key = user.cin || user.id;
          presence[key] = user.presence || false;
        });
        setPresenceMap(presence);
      } else {
        setUsers([]);
      }
    } catch (err) {
      console.error("Erreur chargement utilisateurs:", err);
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };
  
  const handleDateFilterChange = (e) => {
    const date = e.target.value;
    setFilterDate(date);
    // Vider tableData quand on applique un filtre de date pour forcer l'affichage des users filtrés
    if (date) {
      setTableData([]);
      fetchUsers(date);
    } else {
      fetchUsers(); // Recharger tous les utilisateurs si pas de filtre
    }
  };

  const triggerFileDialog = () => {
    document.getElementById("excelInput").click();
  };

  const handleFileSelected = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setSelectedFile(file);
    setImportResult(null);
    
      // Prévisualiser le fichier Excel en l'envoyant au backend pour lecture
      try {
        const formData = new FormData();
        formData.append("file", file);
        
        // Utiliser l'endpoint unifié upload_excel pour la prévisualisation
        const res = await axios.post(
          `${API_BASE}/api/hse/upload_excel/`,
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );
        
        if (res.data.success && res.data.data) {
          // Ne pas remplir tableData si un filtre de date est actif
          if (!filterDate) {
            setTableData(res.data.data);
          }
          // Initialiser la présence pour les nouvelles données Excel
          const presence = {};
          res.data.data.forEach((row, idx) => {
            const cin = (row.cin || row.CIN || row['n°_cin'] || '').toString().toUpperCase();
            if (cin) {
              // Vérifier si l'utilisateur existe déjà dans la base
              const existingUser = users.find(u => u.cin === cin);
              presence[cin] = existingUser ? (existingUser.presence || false) : false;
            }
          });
          setPresenceMap(prev => ({ ...prev, ...presence }));
        }
      } catch (err) {
        // Si l'endpoint n'existe pas, on continue sans prévisualisation
        console.log("Prévisualisation non disponible, importez pour voir les données");
      }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Veuillez sélectionner un fichier Excel.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    setLoading(true);
    setImportResult(null);

    try {
      const res = await axios.post(
        `${API_BASE}/api/users/import/`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      if (res.data.success) {
        setImportResult({
          success: true,
          message: res.data.message,
          summary: res.data.summary,
          errors: res.data.errors || []
        });
        setSelectedFile(null);
        // Afficher les données du fichier Excel importé
        if (res.data.data && res.data.data.length > 0) {
          setTableData(res.data.data);
          // Initialiser la présence pour les données importées
          const presence = {};
          const newUsers = [];
          res.data.data.forEach((row) => {
            const cin = (row.cin || row.CIN || row['n°_cin'] || '').toString().toUpperCase();
            if (cin) {
              // Utiliser la présence de la base si disponible, sinon false
              presence[cin] = row._presence !== undefined ? row._presence : false;
              // Ajouter l'utilisateur à la liste si on a un ID
              if (row._id) {
                newUsers.push({
                  id: row._id,
                  cin: cin,
                  nom: row.nom || row.Nom || '',
                  prénom: row.prénom || row.prenom || row.Prénom || '',
                  entite: row.entite || row.Entité || '',
                  entreprise: row.entreprise || row.Entreprise || '',
                  chef_projet_ocp: row._chef_projet_ocp || row.chef_projet_ocp || row['chef de projet'] || '',
                  presence: row._presence || false
                });
              }
            }
          });
          setPresenceMap(prev => ({ ...prev, ...presence }));
          // Mettre à jour la liste des utilisateurs avec les nouveaux
          if (newUsers.length > 0) {
            setUsers(prevUsers => {
              const updated = [...prevUsers];
              newUsers.forEach(newUser => {
                const index = updated.findIndex(u => u.cin === newUser.cin);
                if (index >= 0) {
                  updated[index] = { ...updated[index], ...newUser };
                } else {
                  updated.push(newUser);
                }
              });
              return updated;
            });
          }
        } else {
          // Si pas de données retournées, recharger depuis la base avec le filtre actif
          await fetchUsers(filterDate || null);
        }
      } else {
        setImportResult({
          success: false,
          message: res.data.error || "Erreur lors de l'import"
        });
      }
    } catch (err) {
      console.error(err);
      setImportResult({
        success: false,
        message: err.response?.data?.error || "Erreur lors de l'import."
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePresenceChange = async (cin, userId, newPresence) => {
    console.log(`[PRESENCE DEBUG] Début - CIN: ${cin}, UserID: ${userId}, Nouvelle présence: ${newPresence}`);
    
    // Déterminer l'ID utilisateur à utiliser
    let finalUserId = userId;
    
    // Si userId n'est pas fourni, chercher dans users
    if (!finalUserId) {
      const foundUser = users.find(u => u.cin === cin);
      if (foundUser && foundUser.id) {
        finalUserId = foundUser.id;
        console.log(`[PRESENCE DEBUG] UserID trouvé dans users: ${finalUserId}`);
      }
    }
    
    // Si toujours pas d'ID, chercher dans tableData
    if (!finalUserId && tableData.length > 0) {
      const foundRow = tableData.find(row => {
        const rowCin = (row.cin || row.CIN || row['n°_cin'] || '').toString().toUpperCase();
        return rowCin === cin;
      });
      if (foundRow && foundRow._id) {
        finalUserId = foundRow._id;
        console.log(`[PRESENCE DEBUG] UserID trouvé dans tableData: ${finalUserId}`);
      }
    }
    
    if (!finalUserId) {
      console.error(`[PRESENCE DEBUG] ERREUR: Aucun UserID trouvé pour CIN: ${cin}`);
      console.error(`[PRESENCE DEBUG] users.length: ${users.length}, tableData.length: ${tableData.length}`);
      alert('Erreur : Utilisateur non trouvé. Veuillez réimporter les données ou recharger la page.');
      return;
    }
    
    // Mettre à jour localement immédiatement pour feedback visuel
    setPresenceMap(prev => ({ ...prev, [cin]: newPresence }));
    
    const url = `${API_BASE}/api/hse/users/${finalUserId}/presence/`;
    const payload = { presence: newPresence };
    
    console.log(`[PRESENCE DEBUG] URL: ${url}`);
    console.log(`[PRESENCE DEBUG] Payload:`, JSON.stringify(payload));
    console.log(`[PRESENCE DEBUG] API_BASE: ${API_BASE}`);
    
    try {
      // Essayer d'abord avec PATCH
      let res;
      try {
        console.log(`[PRESENCE DEBUG] Tentative PATCH...`);
        res = await axios.patch(
          url,
          payload,
          { 
            headers: { 
              'Content-Type': 'application/json',
            },
            timeout: 10000
          }
        );
        console.log(`[PRESENCE DEBUG] PATCH réussi, status: ${res.status}`);
      } catch (patchError) {
        console.warn('[PRESENCE DEBUG] PATCH échoué, essai avec POST:', patchError.message);
        if (patchError.code === 'ERR_NETWORK' || patchError.message.includes('Network Error')) {
          throw new Error('Le serveur Django n\'est pas accessible. Veuillez démarrer le serveur avec: python manage.py runserver');
        }
        // Fallback vers POST
        res = await axios.post(
          url,
          payload,
          { 
            headers: { 
              'Content-Type': 'application/json',
            },
            timeout: 10000
          }
        );
        console.log(`[PRESENCE DEBUG] POST réussi, status: ${res.status}`);
      }
      
      console.log('[PRESENCE DEBUG] Réponse complète:', res);
      console.log('[PRESENCE DEBUG] Réponse data:', res.data);
      console.log('[PRESENCE DEBUG] Status:', res.status);
      
      if (res.data && res.data.success) {
        const confirmedPresence = res.data.user?.presence ?? newPresence;
        
        // Mettre à jour l'utilisateur dans la liste users
        setUsers(prevUsers => {
          const index = prevUsers.findIndex(u => u.cin === cin || u.id === finalUserId);
          if (index >= 0) {
            const updated = [...prevUsers];
            updated[index] = { ...updated[index], presence: confirmedPresence };
            console.log(`[PRESENCE DEBUG] Utilisateur mis à jour dans users[${index}]`);
            return updated;
          } else {
            // Ajouter l'utilisateur s'il n'existe pas encore
            console.log(`[PRESENCE DEBUG] Ajout de l'utilisateur à users`);
            return [...prevUsers, { id: finalUserId, cin: cin, presence: confirmedPresence }];
          }
        });
        
        // Mettre à jour aussi dans tableData si présent
        setTableData(prevData => 
          prevData.map(row => {
            const rowCin = (row.cin || row.CIN || row['n°_cin'] || '').toString().toUpperCase();
            if (rowCin === cin || row._id === finalUserId) {
              console.log(`[PRESENCE DEBUG] Mise à jour tableData pour CIN: ${cin}`);
              return { ...row, _presence: confirmedPresence };
            }
            return row;
          })
        );
        
        // Mettre à jour presenceMap avec la valeur confirmée du serveur
        setPresenceMap(prev => ({ ...prev, [cin]: confirmedPresence }));
        
        console.log(`[PRESENCE DEBUG] ✅ Présence mise à jour avec succès: ${confirmedPresence}`);
      } else {
        // Revert en cas d'erreur
        setPresenceMap(prev => ({ ...prev, [cin]: !newPresence }));
        const errorMsg = res.data?.error || 'Réponse invalide du serveur';
        console.error(`[PRESENCE DEBUG] ❌ Erreur dans la réponse:`, errorMsg);
        alert(`Erreur: ${errorMsg}`);
      }
    } catch (err) {
      // Revert en cas d'erreur
      setPresenceMap(prev => ({ ...prev, [cin]: !newPresence }));
      
      console.error('[PRESENCE DEBUG] ❌ ERREUR COMPLÈTE:', err);
      console.error('[PRESENCE DEBUG] Type erreur:', err.constructor.name);
      console.error('[PRESENCE DEBUG] Code erreur:', err.code);
      console.error('[PRESENCE DEBUG] Message:', err.message);
      console.error('[PRESENCE DEBUG] Status:', err.response?.status);
      console.error('[PRESENCE DEBUG] Détails erreur:', err.response?.data);
      console.error('[PRESENCE DEBUG] Stack:', err.stack);
      
      let errorMsg = 'Erreur inconnue';
      if (err.code === 'ERR_NETWORK' || err.message.includes('Network Error') || err.message.includes('CONNECTION_REFUSED')) {
        errorMsg = 'Le serveur Django n\'est pas accessible. Veuillez démarrer le serveur avec: cd backend && python manage.py runserver';
      } else if (err.response?.data?.error) {
        errorMsg = err.response.data.error;
      } else if (err.response?.data?.message) {
        errorMsg = err.response.data.message;
      } else if (err.message) {
        errorMsg = err.message;
      }
      
      alert(`Erreur lors de la mise à jour de la présence:\n\n${errorMsg}\n\nVérifiez la console pour plus de détails.`);
    }
  };

  const handleDeleteUsers = async () => {
    if (selectedUsers.length === 0) {
      alert('Veuillez sélectionner au moins un utilisateur à supprimer.');
      return;
    }

    if (!confirm(`Êtes-vous sûr de vouloir supprimer ${selectedUsers.length} utilisateur(s) ? Cette action est irréversible.`)) {
      return;
    }

    setLoading(true);
    try {
      // Supprimer chaque utilisateur
      const deletePromises = selectedUsers.map(userId =>
        axios.delete(`${API_BASE}/api/hse/users/${userId}/delete/`)
      );

      const results = await Promise.allSettled(deletePromises);
      const successful = results.filter(r => r.status === 'fulfilled' && r.value.data?.success).length;
      const failed = results.length - successful;

      if (successful > 0) {
        alert(`${successful} utilisateur(s) supprimé(s) avec succès${failed > 0 ? `, ${failed} échec(s)` : ''}.`);
        // Recharger les données
        setSelectedUsers([]);
        if (filterDate) {
          await fetchUsers(filterDate);
        } else {
          await fetchUsers();
        }
        // Vider tableData si nécessaire
        if (tableData.length > 0) {
          setTableData([]);
        }
      } else {
        alert(`Erreur: Aucun utilisateur n'a pu être supprimé.`);
      }
    } catch (err) {
      console.error('Erreur lors de la suppression:', err);
      alert(`Erreur lors de la suppression: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSensibiliseChange = async (cin, userId, newSensibilise) => {
    console.log(`[SENSIBILISE] Mise à jour - CIN: ${cin}, UserID: ${userId}, Nouvelle valeur: ${newSensibilise}`);
    
    let finalUserId = userId;
    if (!finalUserId) {
      const foundUser = users.find(u => u.cin === cin);
      if (foundUser && foundUser.id) {
        finalUserId = foundUser.id;
      }
    }
    
    if (!finalUserId && tableData.length > 0) {
      const foundRow = tableData.find(row => {
        const rowCin = (row.cin || row.CIN || row['n°_cin'] || '').toString().toUpperCase();
        return rowCin === cin;
      });
      if (foundRow && foundRow._id) {
        finalUserId = foundRow._id;
      }
    }
    
    if (!finalUserId) {
      alert('Erreur : Utilisateur non trouvé. Veuillez réimporter les données.');
      return;
    }
    
    const url = `${API_BASE}/api/hse/users/${finalUserId}/sensibilise/`;
    const payload = { sensibilise_avec_succes: newSensibilise };
    
    try {
      let res;
      try {
        res = await axios.patch(url, payload, { 
          headers: { 'Content-Type': 'application/json' },
          timeout: 10000
        });
      } catch (patchError) {
        res = await axios.post(url, payload, { 
          headers: { 'Content-Type': 'application/json' },
          timeout: 10000
        });
      }
      
      if (res.data && res.data.success) {
        const confirmedSensibilise = res.data.user?.sensibilise_avec_succes ?? newSensibilise;
        
        setUsers(prevUsers => {
          const index = prevUsers.findIndex(u => u.cin === cin || u.id === finalUserId);
          if (index >= 0) {
            const updated = [...prevUsers];
            updated[index] = { ...updated[index], sensibilise_avec_succes: confirmedSensibilise };
            return updated;
          }
          return prevUsers;
        });
        
        setTableData(prevData => 
          prevData.map(row => {
            const rowCin = (row.cin || row.CIN || row['n°_cin'] || '').toString().toUpperCase();
            if (rowCin === cin || row._id === finalUserId) {
              return { ...row, _sensibilise_avec_succes: confirmedSensibilise };
            }
            return row;
          })
        );
      } else {
        alert(`Erreur: ${res.data?.error || 'Réponse invalide du serveur'}`);
      }
    } catch (err) {
      console.error('Erreur mise à jour sensibilisation:', err);
      const errorMsg = err.response?.data?.error || err.message || 'Erreur inconnue';
      alert(`Erreur lors de la mise à jour: ${errorMsg}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-300 p-10">
      <TopNav className="mb-4" />

      {/* Header */}
      <div className="flex items-center mb-10">
        <div className="flex items-center gap-3">
          <img src="/ocp-logo.png" alt="logo" className="w-12" />
          <h1 className="text-xl font-bold text-green-900">
            Induction HSE - Jorf Lasfar
          </h1>
        </div>
      </div>

      {/* TITRE */}
      <h2 className="text-3xl font-bold text-gray-800 mb-2">Gestion des Utilisateurs HSE</h2>
      <p className="text-gray-600 mb-6">Importez un fichier Excel pour ajouter ou mettre à jour les utilisateurs.</p>
      
      {/* FILTRE PAR DATE */}
      <div className="bg-white p-4 rounded-lg shadow-md border border-green-200 mb-6">
        <div className="flex items-center gap-4">
          <label htmlFor="dateFilter" className="text-green-700 font-semibold">
            Filtrer par date d'ajout :
          </label>
          <input
            type="date"
            id="dateFilter"
            value={filterDate}
            onChange={handleDateFilterChange}
            className="px-4 py-2 border border-green-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          {filterDate && (
            <button
              onClick={() => {
                setFilterDate('');
                fetchUsers();
              }}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
            >
              Effacer le filtre
            </button>
          )}
        </div>
        {filterDate && (
          <p className="mt-2 text-sm text-gray-600">
            Affichage des utilisateurs ajoutés le <strong>{new Date(filterDate).toLocaleDateString('fr-FR')}</strong>
            {users.length > 0 && <span className="ml-2 text-green-600">({users.length} utilisateur{users.length > 1 ? 's' : ''})</span>}
          </p>
        )}
      </div>
      
      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-900 mb-2">Format du fichier Excel requis :</h3>
        <ul className="text-sm text-blue-800 list-disc list-inside space-y-1">
          <li>Colonnes obligatoires : <strong>CIN</strong>, <strong>nom</strong>, <strong>prénom</strong>, <strong>entite</strong>, <strong>entreprise</strong></li>
          <li>Colonne optionnelle : <strong>chef_projet_ocp</strong></li>
          <li>La première ligne doit contenir les en-têtes (noms des colonnes)</li>
          <li>Chaque CIN doit être unique (pas de doublons dans le fichier)</li>
          <li>Les utilisateurs existants (même CIN) seront mis à jour</li>
          <li><strong>Note :</strong> La colonne "Présence" n'est pas dans le fichier Excel. Elle sera ajoutée automatiquement dans le tableau et pourra être modifiée via les checkboxes après l'import.</li>
        </ul>
      </div>

      {/* BLOC TABLE + BOUTON */}
      <div className="bg-white p-6 rounded-xl shadow-lg border border-green-200">

        <div className="flex justify-between items-center mb-6">
          <h3 className="text-green-700 text-xl font-semibold">Table des données</h3>

          <div className="flex gap-3">
            {/* BOUTON SUPPRIMER */}
            {selectedUsers.length > 0 && (
              <button
                onClick={handleDeleteUsers}
                disabled={loading}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition disabled:opacity-50"
              >
                🗑️ Supprimer ({selectedUsers.length})
              </button>
            )}

            {/* BOUTON IMPORT */}
            <button
              onClick={triggerFileDialog}
              className="bg-green-700 text-white px-4 py-2 rounded-lg hover:bg-green-800 transition"
            >
              + Importer fichier Excel
            </button>
          </div>

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
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-700 mb-3">
              Fichier sélectionné : <strong>{selectedFile.name}</strong>
              {tableData.length > 0 && (
                <span className="ml-2 text-sm text-green-600">
                  ({tableData.length} ligne{tableData.length > 1 ? 's' : ''} détectée{tableData.length > 1 ? 's' : ''})
                </span>
              )}
            </p>
            <button
              onClick={handleUpload}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? "Import en cours..." : "Importer dans la base de données"}
            </button>
          </div>
        )}

        {/* Résultat de l'import */}
        {importResult && (
          <div className={`mb-6 p-4 rounded-lg ${importResult.success ? 'bg-green-50 border border-green-300' : 'bg-red-50 border border-red-300'}`}>
            <p className={importResult.success ? 'text-green-800' : 'text-red-800'}>
              <strong>{importResult.success ? '✓' : '✗'}</strong> {importResult.message}
            </p>
            {importResult.summary && (
              <div className="mt-2 text-sm text-gray-700">
                <p>Créés: {importResult.summary.created} | Mis à jour: {importResult.summary.updated} | Total: {importResult.summary.total_processed}</p>
                {importResult.errors.length > 0 && (
                  <div className="mt-2">
                    <p className="font-semibold">Erreurs:</p>
                    <ul className="list-disc list-inside">
                      {importResult.errors.slice(0, 5).map((err, idx) => (
                        <li key={idx}>{err}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TABLEAU DES DONNÉES EXCEL */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-green-50 text-green-700 font-semibold">
                <th className="p-3 border">
                  <input
                    type="checkbox"
                    onChange={(e) => {
                      if (e.target.checked) {
                        // Sélectionner tous les utilisateurs visibles
                        const visibleUserIds = filterDate && users.length > 0
                          ? users.map(u => u.id)
                          : tableData.length > 0
                          ? tableData.filter(row => {
                              const cin = (row.cin || row.CIN || row['n°_cin'] || '').toString().toUpperCase();
                              const userId = row._id || (users.find(u => u.cin === cin)?.id);
                              return userId;
                            }).map(row => {
                              const cin = (row.cin || row.CIN || row['n°_cin'] || '').toString().toUpperCase();
                              return row._id || (users.find(u => u.cin === cin)?.id);
                            })
                          : users.map(u => u.id);
                        setSelectedUsers(visibleUserIds.filter(id => id));
                      } else {
                        setSelectedUsers([]);
                      }
                    }}
                    checked={selectedUsers.length > 0 && (
                      filterDate && users.length > 0
                        ? selectedUsers.length === users.length
                        : tableData.length > 0
                        ? selectedUsers.length === tableData.filter(row => {
                            const cin = (row.cin || row.CIN || row['n°_cin'] || '').toString().toUpperCase();
                            return row._id || (users.find(u => u.cin === cin)?.id);
                          }).length
                        : selectedUsers.length === users.length
                    )}
                    className="w-4 h-4 cursor-pointer"
                    title="Sélectionner tout"
                  />
                </th>
                <th className="p-3 border">Entité</th>
                <th className="p-3 border">Entreprise</th>                
                <th className="p-3 border">Chef de projet</th>
                <th className="p-3 border">Nom</th>
                <th className="p-3 border">Prénom</th>
                <th className="p-3 border">N°_CIN</th>
                <th className="p-3 border">Présence</th>
                <th className="p-3 border">Sensibilisé avec succès</th>
              </tr>
            </thead>
            <tbody>
              {/* Si un filtre de date est actif, prioriser l'affichage des users filtrés */}
              {filterDate && users.length > 0 ? (
                // Afficher les utilisateurs filtrés par date
                users.map((user) => {
                  const cin = (user.cin || '').toString().toUpperCase();
                  // Priorité: user.presence > presenceMap > false
                  const presence = user.presence !== undefined 
                    ? user.presence 
                    : (presenceMap[cin] !== undefined ? presenceMap[cin] : false);
                  
                  return (
                    <tr key={user.id} className="hover:bg-green-50">
                      <td className="p-3 border text-center">
                        <input
                          type="checkbox"
                          checked={selectedUsers.includes(user.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedUsers(prev => [...prev, user.id]);
                            } else {
                              setSelectedUsers(prev => prev.filter(id => id !== user.id));
                            }
                          }}
                          className="w-4 h-4 cursor-pointer"
                          title="Sélectionner pour suppression"
                        />
                      </td>
                      <td className="p-3 border">{user.entite || ''}</td>
                      <td className="p-3 border">{user.entreprise || ''}</td>
                      <td className="p-3 border">{user.chef_projet_ocp || ''}</td>
                      <td className="p-3 border">{user.nom || ''}</td>
                      <td className="p-3 border">{user.prénom || user.prenom || ''}</td>
                      <td className="p-3 border">{cin}</td>
                      <td className="p-3 border text-center">
                        <input
                          type="checkbox"
                          checked={presence}
                          onChange={(e) => {
                            e.preventDefault();
                            handlePresenceChange(cin, user.id, e.target.checked);
                          }}
                          className="w-5 h-5 cursor-pointer"
                          title="Cliquez pour modifier la présence"
                        />
                      </td>
                      <td className="p-3 border text-center">
                        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          user.sensibilise_avec_succes 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {user.sensibilise_avec_succes ? 'OUI' : 'NON'}
                        </span>
                      </td>
                    </tr>
                  );
                })
              ) : tableData.length > 0 ? (
                tableData.map((row, idx) => {
                  // Normaliser les noms de colonnes (insensible à la casse)
                  const getValue = (key) => {
                    const keys = Object.keys(row);
                    const foundKey = keys.find(k => k.toLowerCase() === key.toLowerCase());
                    return row[foundKey] || '';
                  };
                  
                  const cin = (getValue('cin') || getValue('CIN') || getValue('n°_cin') || '').toString().toUpperCase();
                  // Utiliser _id si disponible (depuis l'import), sinon chercher dans users
                  const userId = row._id || (users.find(u => u.cin === cin)?.id);
                  // Trouver l'utilisateur dans la liste pour obtenir la présence à jour
                  const userFromList = users.find(u => u.cin === cin);
                  // Priorité: userFromList > presenceMap > row._presence > false
                  const presence = userFromList?.presence !== undefined 
                    ? userFromList.presence 
                    : (presenceMap[cin] !== undefined 
                      ? presenceMap[cin] 
                      : (row._presence !== undefined ? row._presence : false));
                  // Récupérer chef_projet_ocp depuis les données importées ou depuis la base
                  const chefProjet = row._chef_projet_ocp !== undefined ? row._chef_projet_ocp : 
                                    (getValue('chef_projet_ocp') || getValue('chef de projet') || getValue('chef_projet') || 
                                     (userFromList?.chef_projet_ocp) || '');
                  
                  return (
                    <tr key={idx} className="hover:bg-green-50">
                      <td className="p-3 border text-center">
                        {userId && (
                          <input
                            type="checkbox"
                            checked={selectedUsers.includes(userId)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedUsers(prev => [...prev, userId]);
                              } else {
                                setSelectedUsers(prev => prev.filter(id => id !== userId));
                              }
                            }}
                            className="w-4 h-4 cursor-pointer"
                            title="Sélectionner pour suppression"
                          />
                        )}
                      </td>
                      <td className="p-3 border">{getValue('entite') || getValue('entité')}</td>
                      <td className="p-3 border">{getValue('entreprise')}</td>
                      <td className="p-3 border">{chefProjet}</td>
                      <td className="p-3 border">{getValue('nom')}</td>
                      <td className="p-3 border">{getValue('prénom') || getValue('prenom')}</td>
                      <td className="p-3 border">{cin}</td>
                      <td className="p-3 border text-center">
                        <input
                          type="checkbox"
                          checked={presence}
                          onChange={(e) => {
                            e.preventDefault();
                            handlePresenceChange(cin, userId, e.target.checked);
                          }}
                          disabled={!userId}
                          className="w-5 h-5 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                          title={userId ? "Cliquez pour modifier la présence" : "Importez d'abord les données pour activer cette fonctionnalité"}
                        />
                      </td>
                      <td className="p-3 border text-center">
                        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          userFromList?.sensibilise_avec_succes 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {userFromList?.sensibilise_avec_succes ? 'OUI' : 'NON'}
                        </span>
                      </td>
                    </tr>
                  );
                })
              ) : users.length > 0 ? (
                // Fallback : afficher les utilisateurs de la base si pas de données Excel
                users.map((user) => {
                  const cin = (user.cin || '').toString().toUpperCase();
                  const presence = presenceMap[cin] !== undefined ? presenceMap[cin] : (user.presence || false);
                  
                  return (
                    <tr key={user.id} className="hover:bg-green-50">
                      <td className="p-3 border text-center">
                        <input
                          type="checkbox"
                          checked={selectedUsers.includes(user.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedUsers(prev => [...prev, user.id]);
                            } else {
                              setSelectedUsers(prev => prev.filter(id => id !== user.id));
                            }
                          }}
                          className="w-4 h-4 cursor-pointer"
                          title="Sélectionner pour suppression"
                        />
                      </td>
                      <td className="p-3 border">{user.entite || ''}</td>
                      <td className="p-3 border">{user.entreprise || ''}</td>
                      <td className="p-3 border">{user.chef_projet_ocp || ''}</td>
                      <td className="p-3 border">{user.nom || ''}</td>
                      <td className="p-3 border">{user.prénom || user.prenom || ''}</td>
                      <td className="p-3 border">{cin}</td>
                      <td className="p-3 border text-center">
                        <input
                          type="checkbox"
                          checked={presence}
                          onChange={(e) => handlePresenceChange(cin, user.id, e.target.checked)}
                          className="w-5 h-5 cursor-pointer"
                          title="Cliquez pour modifier la présence"
                        />
                      </td>
                      <td className="p-3 border text-center">
                        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          user.sensibilise_avec_succes 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {user.sensibilise_avec_succes ? 'OUI' : 'NON'}
                        </span>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan="9" className="p-4 text-center text-gray-500">
                    {filterDate 
                      ? `Aucun utilisateur ajouté le ${new Date(filterDate).toLocaleDateString('fr-FR')}.`
                      : "Aucune donnée disponible. Importez un fichier Excel pour commencer."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          {loading && <p className="text-center py-4 text-gray-600">Chargement...</p>}
        </div>

      </div>

      {/* FOOTER */}
      <footer className="text-center mt-20 text-gray-600 text-sm">
        © 2025 OCP – Portail Interne HSE. Tous droits réservés.
      </footer>
    </div>
  );
}
