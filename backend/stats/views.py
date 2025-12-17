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
    try:
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
            try:
                day = int(day)
                month = int(month)
                year = int(year)
            except (ValueError, TypeError):
                return JsonResponse({
                    "error": "Date invalide",
                    "presence": 0,
                    "test_initial": 0,
                    "test_final": 0
                }, status=400)

        try:
            selected_date = datetime.date(year, month, day)
        except ValueError:
            return JsonResponse({
                "error": "Date invalide",
                "presence": 0,
                "test_initial": 0,
                "test_final": 0
            }, status=400)

        # 3️⃣ Importer les modèles
        from hse_app.models import HSEUser
        from tests.models import TestAttempt
        
        # 4️⃣ Calculer le pourcentage de présence pour le jour sélectionné
        # Compter tous les utilisateurs ajoutés à cette date (ou avant cette date pour inclure tous les utilisateurs pertinents)
        try:
            # Filtrer les utilisateurs ajoutés à cette date
            users_for_date = HSEUser.objects.filter(date_ajout=selected_date)
            total_users = users_for_date.count()
            
            # Compter ceux qui ont presence=True
            # Utiliser .filter() avec presence=True pour s'assurer que le filtre fonctionne correctement
            present_users = users_for_date.filter(presence=True).count()
            
            # Debug: afficher les valeurs pour vérifier
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"[STATS] Date: {selected_date}, Total users: {total_users}, Present users: {present_users}")
            
            # S'assurer que presence_percentage est toujours un nombre
            if total_users > 0:
                presence_percentage = (present_users / total_users) * 100
            else:
                presence_percentage = 0.0
        except Exception as e:
            # En cas d'erreur, retourner 0
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur calcul présence: {str(e)}")
            presence_percentage = 0.0
            total_users = 0
            present_users = 0
        
        # 5️⃣ Calculer la moyenne des tests pour le jour sélectionné
        # Filtrer uniquement les tests terminés pendant ce jour (completed_at à cette date)
        try:
            attempts_for_date = TestAttempt.objects.filter(
                completed_at__date=selected_date,
                completed_at__isnull=False,
                status__in=['passed', 'failed']
            )
            total_attempts = attempts_for_date.count()
            
            if total_attempts > 0:
                # Calculer la moyenne des scores globaux (overall_score_percentage)
                total_score = sum(attempt.overall_score_percentage or 0 for attempt in attempts_for_date)
                average_test_score = total_score / total_attempts
            else:
                average_test_score = 0.0
        except Exception as e:
            # En cas d'erreur, retourner 0
            average_test_score = 0.0
            total_attempts = 0
        
        # 6️⃣ Retour JSON parfait pour React - s'assurer que toutes les valeurs sont des nombres
        return JsonResponse({
            "presence": float(round(presence_percentage, 2)),
            "presence_count": int(present_users),
            "total_users": int(total_users),
            "average_test_score": float(round(average_test_score, 2)),
            "total_attempts": int(total_attempts),
            "test_initial": 0.0,  # Pour compatibilité avec l'ancien code
            "test_final": float(round(average_test_score, 2)),
            "improvement": float(round(average_test_score, 2)),
            "date": selected_date.isoformat()
        })
    except Exception as e:
        # Gestion d'erreur globale
        import traceback
        print(f"Erreur dans hse_stats: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            "error": "Erreur serveur",
            "presence": 0,
            "presence_count": 0,
            "total_users": 0,
            "average_test_score": 0,
            "total_attempts": 0,
            "test_initial": 0,
            "test_final": 0,
            "improvement": 0
        }, status=500)


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
