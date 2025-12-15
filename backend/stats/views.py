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
    Utilise les données de la base de données (HSEUser et TestAttempt).
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
    else:
        day = int(day)
        month = int(month)
        year = int(year)

    try:
        selected_date = datetime.date(year, month, day)
    except ValueError:
        return JsonResponse({
            "error": "Date invalide"
        }, status=400)

    # 3️⃣ Importer les modèles
    from hse_app.models import HSEUser
    from tests.models import TestAttempt
    
    # 4️⃣ Calculer le pourcentage de présence pour le jour sélectionné
    users_for_date = HSEUser.objects.filter(date_ajout=selected_date)
    total_users = users_for_date.count()
    present_users = users_for_date.filter(presence=True).count()
    presence_percentage = (present_users / total_users * 100) if total_users > 0 else 0
    
    # 5️⃣ Calculer la moyenne des tests pour le jour sélectionné
    # Filtrer uniquement les tests terminés pendant ce jour (completed_at à cette date)
    attempts_for_date = TestAttempt.objects.filter(
        completed_at__date=selected_date,
        completed_at__isnull=False,
        status__in=['passed', 'failed']
    )
    total_attempts = attempts_for_date.count()
    
    if total_attempts > 0:
        # Calculer la moyenne des scores globaux (overall_score_percentage)
        total_score = sum(attempt.overall_score_percentage for attempt in attempts_for_date)
        average_test_score = total_score / total_attempts
    else:
        average_test_score = 0
    
    # 6️⃣ Retour JSON parfait pour React
    return JsonResponse({
        "presence": round(presence_percentage, 2),
        "presence_count": present_users,
        "total_users": total_users,
        "average_test_score": round(average_test_score, 2),
        "total_attempts": total_attempts,
        "test_initial": 0,  # Pour compatibilité avec l'ancien code
        "test_final": round(average_test_score, 2),
        "improvement": round(average_test_score, 2),
        "date": selected_date.isoformat()
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
