import pandas as pd
from django.db import transaction
from hse_app.models import HSEUser

def import_hse_users_excel(excel_file):
    """
    Importer des utilisateurs HSE depuis un fichier Excel.
    Le fichier doit contenir les colonnes correspondant aux champs de HSEUser :
    - CIN (obligatoire, unique)
    - nom
    - prénom
    - entite
    - entreprise
    - chef_projet_ocp (optionnel)
    
    Note: Le champ 'presence' n'est PAS importé depuis le fichier Excel.
    Il sera défini à False par défaut et pourra être modifié ensuite par un manager.
    """
    try:
        # Lire sans header pour trouver la ligne d'en-tête
        df_raw = pd.read_excel(excel_file, header=None)
        
        # Trouver la ligne contenant "Entité" (l'en-tête réelle)
        header_row = None
        for i, row in df_raw.iterrows():
            if row.astype(str).str.contains("Entité", case=False, na=False).any():
                header_row = i
                break
        
        if header_row is None:
            return {
                "status": "error",
                "message": "Impossible de trouver l'en-tête 'Entité' dans ce fichier."
            }
        
        # Recharger le fichier en utilisant la ligne trouvée comme header
        excel_file.seek(0)  # Réinitialiser le pointeur du fichier
        df = pd.read_excel(excel_file, header=header_row)
        
        # Supprimer colonnes 'Unnamed'
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # Supprimer lignes vides
        df = df.dropna(how="all")
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Normalisation des noms de colonnes (insensible à la casse, enlever accents)
        # Créer un mapping pour normaliser les colonnes
        column_mapping = {}
        for col in df.columns:
            col_lower = str(col).strip().lower()
            # Normaliser les accents et caractères spéciaux
            col_normalized = col_lower.replace('é', 'e').replace('è', 'e').replace('ê', 'e')
            col_normalized = col_normalized.replace('à', 'a').replace('â', 'a')
            col_normalized = col_normalized.replace('ù', 'u').replace('û', 'u')
            col_normalized = col_normalized.replace('ô', 'o').replace('ö', 'o')
            col_normalized = col_normalized.replace('î', 'i').replace('ï', 'i')
            col_normalized = col_normalized.replace('ç', 'c')
            # Enlever espaces et caractères spéciaux
            col_normalized = col_normalized.replace(' ', '_').replace('-', '_')
            col_normalized = col_normalized.replace('°', '').replace('n°', 'n')
            column_mapping[col] = col_normalized
        
        # Renommer les colonnes
        df = df.rename(columns=column_mapping)
        
        # Vérification des colonnes obligatoires (avec différentes variantes possibles)
        # Fonction pour normaliser une chaîne pour comparaison
        def normalize_for_comparison(s):
            s = str(s).strip().lower()
            s = s.replace('é', 'e').replace('è', 'e').replace('ê', 'e')
            s = s.replace('à', 'a').replace('â', 'a')
            s = s.replace('ù', 'u').replace('û', 'u')
            s = s.replace('ô', 'o').replace('ö', 'o')
            s = s.replace('î', 'i').replace('ï', 'i')
            s = s.replace('ç', 'c')
            s = s.replace(' ', '_').replace('-', '_')
            s = s.replace('°', '').replace('n°', 'n')
            return s
        
        required_columns_map = {
            'cin': ['cin', 'n_cin', 'ncin', 'numero_cin', 'n°_cin'],
            'nom': ['nom', 'name', 'lastname'],
            'prénom': ['prénom', 'prenom', 'firstname'],
            'entite': ['entite', 'entité', 'entity'],
            'entreprise': ['entreprise', 'company', 'societe', 'société']
        }
        
        # Vérifier si on a les colonnes requises (avec leurs variantes)
        missing_columns = []
        found_columns = {}
        
        for required_key, variants in required_columns_map.items():
            found = False
            # Chercher dans les colonnes normalisées
            for col in df.columns:
                col_normalized = normalize_for_comparison(col)
                for variant in variants:
                    variant_normalized = normalize_for_comparison(variant)
                    if col_normalized == variant_normalized:
                        found_columns[required_key] = col
                        found = True
                        break
                if found:
                    break
            if not found:
                missing_columns.append(required_key)
        
        if missing_columns:
            return {
                "status": "error",
                "message": f"Colonnes manquantes dans le fichier : {', '.join(missing_columns)}. "
                           f"Colonnes requises : {', '.join(required_columns_map.keys())}. "
                           f"Colonnes trouvées : {', '.join(df.columns.tolist())}"
            }
        
        # Renommer les colonnes trouvées vers les noms standardisés
        rename_dict = {v: k for k, v in found_columns.items()}
        df = df.rename(columns=rename_dict)
        
        # Vérifier que toutes les colonnes requises sont maintenant présentes
        required_final = ['cin', 'nom', 'prénom', 'entite', 'entreprise']
        missing_final = [col for col in required_final if col not in df.columns]
        if missing_final:
            return {
                "status": "error",
                "message": f"Erreur lors du renommage des colonnes. Colonnes manquantes après normalisation : {', '.join(missing_final)}. "
                           f"Colonnes actuelles : {', '.join(df.columns.tolist())}"
            }
        
        created_count = 0
        updated_count = 0
        errors = []
        duplicate_cins = []
        
        # Collecter tous les CIN pour détecter les doublons dans le fichier
        cins_in_file = df['cin'].astype(str).str.strip().str.upper()
        duplicate_in_file = cins_in_file[cins_in_file.duplicated()].unique().tolist()
        
        if duplicate_in_file:
            return {
                "status": "error",
                "message": f"Doublons de CIN détectés dans le fichier : {', '.join(duplicate_in_file)}. "
                           f"Chaque CIN doit être unique."
            }
        
        # Vérifier les variantes possibles pour chef_projet_ocp
        chef_projet_col = None
        for col in df.columns:
            col_lower = str(col).lower()
            if 'chef' in col_lower and ('projet' in col_lower or 'project' in col_lower):
                chef_projet_col = col
                break
        
        # Transaction => si une ligne pose problème, rien n'est enregistré
        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    cin = str(row.get('cin', '')).strip().upper()
                    nom = str(row.get('nom', '')).strip()
                    prénom = str(row.get('prénom', '')).strip()
                    entite = str(row.get('entite', '')).strip()
                    entreprise = str(row.get('entreprise', '')).strip()
                    chef_projet_ocp = str(row.get(chef_projet_col, '')).strip() if chef_projet_col and chef_projet_col in df.columns else ''
        
                    
                    # Validation CIN
                    if not cin:
                        errors.append(f"Ligne {idx + 2} : CIN manquant")
                        continue
                    
                    # Vérifier si l'utilisateur existe déjà (par CIN)
                    existing_user = HSEUser.objects.filter(cin=cin).first()
                    
                    if existing_user:
                        # Mise à jour des champs (sauf presence qui est géré séparément)
                        existing_user.nom = nom or existing_user.nom
                        existing_user.prénom = prénom or existing_user.prénom
                        existing_user.entite = entite or existing_user.entite
                        existing_user.entreprise = entreprise or existing_user.entreprise
                        if chef_projet_ocp:
                            existing_user.chef_projet_ocp = chef_projet_ocp
                        # Note: presence n'est pas modifié lors de l'import Excel
                        existing_user.save()
                        updated_count += 1
                    else:
                        # Création d'un nouvel utilisateur (presence = False par défaut)
                        HSEUser.objects.create(
                            cin=cin,
                            nom=nom,
                            prénom=prénom,
                            entite=entite,
                            entreprise=entreprise,
                            chef_projet_ocp=chef_projet_ocp,
                            presence=False  # Toujours False lors de l'import
                        )
                        created_count += 1
                        
                except Exception as e:
                    errors.append(f"Ligne {idx + 2} (CIN: {row.get('cin', 'N/A')}) : {str(e)}")
        
        # Récupérer les utilisateurs créés/mis à jour avec leurs IDs pour le frontend
        imported_users = []
        for idx, row in df.iterrows():
            try:
                cin = str(row.get('cin', '')).strip().upper()
                if cin:
                    user = HSEUser.objects.filter(cin=cin).first()
                    if user:
                        imported_users.append({
                            'id': user.id,
                            'cin': user.cin,
                            'presence': user.presence
                        })
            except Exception:
                pass
        
        # Convertir le DataFrame en liste de dictionnaires pour l'affichage
        data_list = df.to_dict('records')
        
        # Ajouter les IDs, présence et chef_projet_ocp aux données pour le frontend
        for data_row in data_list:
            # Les colonnes sont normalisées en minuscules, donc chercher 'cin' directement
            cin = str(data_row.get('cin', '')).strip().upper()
            if cin:
                user_info = next((u for u in imported_users if u['cin'] == cin), None)
                if user_info:
                    data_row['_id'] = user_info['id']
                    data_row['_presence'] = user_info['presence']
                    # Récupérer le chef_projet_ocp depuis la base de données
                    user_obj = HSEUser.objects.filter(cin=cin).first()
                    if user_obj:
                        data_row['_chef_projet_ocp'] = user_obj.chef_projet_ocp or ''
        
        return {
            "status": "success",
            "created": created_count,
            "updated": updated_count,
            "errors": errors,
            "total_processed": len(df),
            "data": data_list,  # Retourner les données du fichier Excel avec IDs
            "imported_users": imported_users  # Liste des utilisateurs avec IDs
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la lecture du fichier : {str(e)}"
        }

