import pandas as pd
from django.db import transaction
from authentication.models import TestUser  

def importexcel(excel_file):
    """
    Importer une liste d'apprenants (HSE Users) depuis un fichier Excel.
    Le fichier doit contenir les colonnes : CIN, FULL_NAME
    """
    try:
        # Lecture du fichier Excel
        df = pd.read_excel(excel_file)

        # Vérification des colonnes obligatoires
        if not {"cin", "full_name"}.issubset(df.columns.str.lower()):
            return {
                "status": "error",
                "message": "Le fichier doit contenir les colonnes CIN et FULL_NAME."
            }

        # Normalisation des noms de colonnes
        df.columns = df.columns.str.lower()

        created_count = 0
        updated_count = 0
        errors = []

        # Transaction => si une ligne pose problème, rien n'est enregistré
        with transaction.atomic():
            for _, row in df.iterrows():
                cin = str(row.get("cin", "")).strip()
                full_name = str(row.get("full_name", "")).strip()

                if not cin:
                    errors.append(f"Ligne invalide : CIN manquant")
                    continue

                try:
                    # Vérifier si l'utilisateur existe déjà
                    user = TestUser.objects.filter(cin=cin).first()

                    if user:
                        # Mise à jour du nom complet si vide
                        if not user.full_name and full_name:
                            user.full_name = full_name
                            user.save()
                            updated_count += 1
                        else:
                            # L'utilisateur existe déjà → ne pas recréer
                            updated_count += 1
                    else:
                        # Création d'un nouvel apprenant (user_type='user')
                        TestUser.objects.create_hse_user(cin=cin, full_name=full_name)
                        created_count += 1

                except Exception as e:
                    errors.append(f"Erreur ligne CIN={cin} : {str(e)}")

        return {
            "status": "success",
            "created": created_count,
            "updated": updated_count,
            "errors": errors
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
