from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import pandas as pd
import datetime
import os


# ------------------------------
#  PAGE HTML CLASSIQUE (optionnel pour toi)
# ------------------------------

def hse_dashboard(request):
    return render(request, 'hse/stats.html', {
        'page_title': 'Induction HSE - Jorf Lasfar',
        'year': 2025
    })


# ------------------------------
#  API : Questionnaires + certificats (déjà fourni)
# ------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class HSEApiView(View):
    def get(self, request, *args, **kwargs):

        questionnaires = [
            {
                'id': 1,
                'titre': 'Test HSE Basique',
                'description': 'Questionnaire de base sur la sécurité',
                'duree': 30,
                'questions_count': 20
            },
            {
                'id': 2,
                'titre': 'Formation Avancée',
                'description': 'Test avancé sur les procédures HSE',
                'duree': 45,
                'questions_count': 30
            }
        ]
        
        return JsonResponse({
            'questionnaires': questionnaires,
            'statistiques': {
                'tests_completes': 0,
                'certificats_generes': 0
            }
        })


# ------------------------------
#  API STATISTIQUES HSE POUR REACT
#  (C’est ici que ton Dashboard HSE vient chercher les données)
# ------------------------------

def hse_stats(request):
    """
    Retourne les statistiques HSE sous forme JSON
    pour le frontend React.
    """

    # 1️⃣ Lire la date passée dans l'URL
    day = request.GET.get("day")
    month = request.GET.get("month")
    year = request.GET.get("year")

    # 2️⃣ Si aucune date → date d'aujourd'hui
    if not (day and month and year):
        today = datetime.date.today()
        day = today.day
        month = today.month
        year = today.year

    # 3️⃣ Construire le chemin du fichier Excel
    file_path = f"backend/data/{day}-{month}-{year}.xlsx"

    if not os.path.exists(file_path):
        return JsonResponse({
            "error": "Fichier du jour introuvable",
            "file_searched": file_path
        }, status=404)

    # 4️⃣ Charger Excel
    df = pd.read_excel(file_path)

    # 5️⃣ Exemple de calculs
    presence = int(df["Présence"].mean() * 100)
    test_initial = int(df["Test initial"].mean() * 100)
    test_final = int(df["Test final"].mean() * 100)

    # 6️⃣ Retour JSON parfait pour React
    return JsonResponse({
        "presence": presence,
        "test_initial": test_initial,
        "test_final": test_final,
        "improvement": test_final - test_initial
    })


# ------------------------------
#  HTML optionnel
# ------------------------------

def gestion_questionnaires(request):
    return render(request, 'hse/gestion_questionnaires.html')

def generation_certificats(request):
    return render(request, 'hse/generation_certificats.html')



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd

@csrf_exempt
def upload_excel(request):
    if request.method == "POST":
        excel_file = request.FILES.get("file")

        if not excel_file:
            return JsonResponse({"success": False, "error": "Aucun fichier reçu"})

        try:
            # Lire sans header
            df_raw = pd.read_excel(excel_file, header=None)

            # Trouver la ligne contenant "Entité" (l'en-tête réelle)
            header_row = None
            for i, row in df_raw.iterrows():
                if row.astype(str).str.contains("Entité").any():
                    header_row = i
                    break

            if header_row is None:
                return JsonResponse({"success": False, "error": "Impossible de trouver l'en-tête dans ce fichier."})

            # Recharger le fichier en utilisant la ligne trouvée comme header
            df = pd.read_excel(excel_file, header=header_row)

            # Supprimer colonnes 'Unnamed'
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

            # Supprimer lignes vides
            df = df.dropna(how="all")

            # Reset index
            df = df.reset_index(drop=True)

            return JsonResponse({"success": True, "data": df.to_dict(orient="records")})

        except Exception as e:
            print("🔥 ERREUR DJANGO :", e)
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Méthode non autorisée"})
