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
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Filtrer les utilisateurs ajoutés à cette date
            users_for_date = HSEUser.objects.filter(date_ajout=selected_date)
            total_users = users_for_date.count()
            
            logger.info(f"[STATS] Calcul présence pour date: {selected_date}")
            logger.info(f"[STATS] Nombre total d'utilisateurs pour cette date: {total_users}")
            
            # Compter ceux qui ont presence=True
            # Utiliser plusieurs méthodes pour s'assurer que le filtre fonctionne
            from django.db.models import Q
            
            # Méthode 1: Filtrer directement
            present_users_query = users_for_date.filter(presence=True)
            present_users = present_users_query.count()
            
            # Méthode 2: Compter manuellement pour vérifier
            present_users_manual = 0
            for user in users_for_date:
                if user.presence is True or user.presence == 1:
                    present_users_manual += 1
            
            logger.info(f"[STATS] Présents (via query): {present_users}, Présents (manuel): {present_users_manual}")
            
            # Utiliser la valeur la plus élevée pour éviter les problèmes de filtre
            present_users = max(present_users, present_users_manual)
            
            # Debug: afficher quelques exemples
            if total_users > 0:
                sample_users = list(users_for_date[:5])
                for user in sample_users:
                    logger.info(f"[STATS DEBUG] User {user.cin} ({user.nom} {user.prénom}): presence={user.presence} (type: {type(user.presence).__name__})")
            
            # S'assurer que presence_percentage est toujours un nombre
            if total_users > 0:
                presence_percentage = (present_users / total_users) * 100
                logger.info(f"[STATS] Pourcentage calculé: {presence_percentage}% ({present_users}/{total_users})")
            else:
                presence_percentage = 0.0
                logger.warning(f"[STATS] Aucun utilisateur trouvé pour la date {selected_date}")
                
        except Exception as e:
            # En cas d'erreur, retourner 0
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur calcul présence: {str(e)}")
            logger.error(traceback.format_exc())
            presence_percentage = 0.0
            total_users = 0
            present_users = 0
        
        # 5️⃣ Calculer la moyenne des tests pour le jour sélectionné
        # Utiliser les données de la table test_attempt
        # Initialiser les variables avant le try
        average_test_score = 0.0
        average_initial_score = 0.0
        average_final_score = 0.0
        total_attempts = 0
        
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Récupérer tous les tests terminés ce jour
            # Utiliser completed_at si disponible, sinon started_at
            # Inclure tous les statuts terminés (passed, failed) et aussi ceux avec un score
            from django.db.models import Q
            
            # Essayer d'abord avec completed_at
            attempts_with_completed = TestAttempt.objects.filter(
                completed_at__date=selected_date,
                completed_at__isnull=False
            ).exclude(status='in_progress')
            
            # Si aucune tentative avec completed_at, utiliser started_at
            attempts_with_started = TestAttempt.objects.filter(
                started_at__date=selected_date,
                completed_at__isnull=True
            ).exclude(status='in_progress')
            
            # Combiner les deux querysets avec union
            attempts_for_date = (attempts_with_completed | attempts_with_started).distinct()
            
            # Si toujours rien, essayer toutes les tentatives de cette date (peu importe le statut)
            if attempts_for_date.count() == 0:
                all_attempts_date = TestAttempt.objects.filter(
                    Q(completed_at__date=selected_date) | Q(started_at__date=selected_date)
                ).distinct()
                logger.warning(f"[STATS] Aucune tentative terminée trouvée, utilisation de toutes les tentatives: {all_attempts_date.count()}")
                attempts_for_date = all_attempts_date
            
            logger.info(f"[STATS] Tentatives avec completed_at: {attempts_with_completed.count()}, avec started_at uniquement: {attempts_with_started.count()}, total: {attempts_for_date.count()}")
            
            total_attempts = attempts_for_date.count()
            
            logger.info(f"[STATS] Tentatives de test pour {selected_date}: {total_attempts}")
            
            # Debug: afficher quelques exemples de tentatives
            if total_attempts > 0:
                sample_attempts = list(attempts_for_date[:3])
                for attempt in sample_attempts:
                    logger.info(f"[STATS DEBUG] Attempt {attempt.id}: etat={attempt.etat}, score={attempt.overall_score_percentage}, status={attempt.status}, completed_at={attempt.completed_at}")
            
            # Séparer les tests initiaux et finaux
            initial_attempts = attempts_for_date.filter(etat='test_initial')
            final_attempts = attempts_for_date.filter(etat='test_final')
            
            initial_count = initial_attempts.count()
            final_count = final_attempts.count()
            
            logger.info(f"[STATS] Tests initiaux: {initial_count}, Tests finaux: {final_count}")
            
            # Fonction helper pour calculer le score d'une tentative
            def get_attempt_score(attempt):
                """Récupère le score d'une tentative, avec fallback si nécessaire"""
                # Priorité 1: overall_score_percentage
                if attempt.overall_score_percentage is not None and attempt.overall_score_percentage >= 0:
                    return attempt.overall_score_percentage
                
                # Priorité 2: Calculer depuis mandatory et optional
                total_questions = (attempt.mandatory_total or 0) + (attempt.optional_total or 0)
                if total_questions > 0:
                    correct_answers = (attempt.mandatory_correct or 0) + (attempt.optional_correct or 0)
                    calculated_score = (correct_answers / total_questions) * 100
                    logger.info(f"[STATS] Score calculé pour attempt {attempt.id}: {calculated_score}% (correct: {correct_answers}/{total_questions})")
                    return calculated_score
                
                # Priorité 3: Utiliser le status (passed = 100%, failed = 0%)
                if attempt.status == 'passed':
                    return 100.0
                elif attempt.status == 'failed':
                    return 0.0
                
                return None
            
            # Calculer la moyenne pour les tests initiaux
            # Utiliser overall_score_percentage depuis la table test_attempt
            if initial_count > 0:
                initial_scores = []
                for attempt in initial_attempts:
                    score = get_attempt_score(attempt)
                    if score is not None and score >= 0:
                        initial_scores.append(score)
                
                if initial_scores:
                    initial_total_score = sum(initial_scores)
                    average_initial_score = initial_total_score / len(initial_scores)
                    logger.info(f"[STATS] Scores initiaux trouvés: {initial_scores}, moyenne: {average_initial_score}")
                else:
                    average_initial_score = 0.0
                    logger.warning(f"[STATS] Aucun score valide pour les tests initiaux")
            else:
                average_initial_score = 0.0
            
            # Calculer la moyenne pour les tests finaux
            # Utiliser overall_score_percentage depuis la table test_attempt
            if final_count > 0:
                final_scores = []
                for attempt in final_attempts:
                    score = get_attempt_score(attempt)
                    if score is not None and score >= 0:
                        final_scores.append(score)
                
                if final_scores:
                    final_total_score = sum(final_scores)
                    average_final_score = final_total_score / len(final_scores)
                    logger.info(f"[STATS] Scores finaux trouvés: {final_scores}, moyenne: {average_final_score}")
                else:
                    average_final_score = 0.0
                    logger.warning(f"[STATS] Aucun score valide pour les tests finaux")
            else:
                average_final_score = 0.0
            
            # Moyenne globale (tous tests confondus)
            if total_attempts > 0:
                all_scores = []
                for attempt in attempts_for_date:
                    score = get_attempt_score(attempt)
                    if score is not None and score >= 0:
                        all_scores.append(score)
                
                if all_scores:
                    total_score = sum(all_scores)
                    average_test_score = total_score / len(all_scores)
                    logger.info(f"[STATS] Scores globaux: {len(all_scores)}/{total_attempts} tentatives avec score valide, moyenne: {average_test_score}")
                else:
                    average_test_score = 0.0
                    logger.warning(f"[STATS] Aucun score valide pour toutes les tentatives")
            else:
                average_test_score = 0.0
                
            logger.info(f"[STATS] Scores finaux - Initial: {average_initial_score}%, Final: {average_final_score}%, Global: {average_test_score}%")
            
        except Exception as e:
            # En cas d'erreur, retourner 0
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur calcul tests: {str(e)}")
            logger.error(traceback.format_exc())
            average_test_score = 0.0
            average_initial_score = 0.0
            average_final_score = 0.0
            total_attempts = 0
        
        # 6️⃣ Retour JSON parfait pour React - s'assurer que toutes les valeurs sont des nombres
        # Calculer l'amélioration (différence entre test final et initial)
        improvement = float(round(average_final_score - average_initial_score, 2))
        
        return JsonResponse({
            "presence": float(round(presence_percentage, 2)),
            "presence_count": int(present_users),
            "total_users": int(total_users),
            "average_test_score": float(round(average_test_score, 2)),
            "total_attempts": int(total_attempts),
            "test_initial": float(round(average_initial_score, 2)),
            "test_final": float(round(average_final_score, 2)),
            "improvement": improvement,
            "date": selected_date.isoformat()
        })
    except Exception as e:
        # Gestion d'erreur globale
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur dans hse_stats: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"Erreur dans hse_stats: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            "error": "Erreur serveur",
            "presence": 0.0,
            "presence_count": 0,
            "total_users": 0,
            "average_test_score": 0.0,
            "total_attempts": 0,
            "test_initial": 0.0,
            "test_final": 0.0,
            "improvement": 0.0
            }, status=500)


@csrf_exempt
def hse_stats_monthly(request):
    """
    Retourne les statistiques HSE pour un mois complet
    GET: /api/stats/hse/stats/monthly/?month=12&year=2025
    Retourne les moyennes quotidiennes des tests initiaux et finaux pour chaque jour du mois
    """
    try:
        import datetime
        from hse_app.models import HSEUser
        from tests.models import TestAttempt
        from django.db.models import Q
        
        # Lire les paramètres
        month = request.GET.get("month")
        year = request.GET.get("year")
        
        # Si non fourni, utiliser le mois actuel
        if not (month and year):
            today = datetime.date.today()
            month = today.month
            year = today.year
        else:
            try:
                month = int(month)
                year = int(year)
            except (ValueError, TypeError):
                return JsonResponse({
                    "error": "Mois ou année invalide"
                }, status=400)
        
        # Vérifier que le mois est valide
        try:
            first_day = datetime.date(year, month, 1)
        except ValueError:
            return JsonResponse({
                "error": "Date invalide"
            }, status=400)
        
        # Calculer le dernier jour du mois
        if month == 12:
            last_day = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        
        # Helper pour obtenir le score d'une tentative
        def get_attempt_score(attempt):
            if attempt.overall_score_percentage is not None and attempt.overall_score_percentage >= 0:
                return attempt.overall_score_percentage
            
            total_questions_attempted = (attempt.mandatory_total or 0) + (attempt.optional_total or 0)
            if total_questions_attempted > 0:
                correct_answers = (attempt.mandatory_correct or 0) + (attempt.optional_correct or 0)
                return (correct_answers / total_questions_attempted) * 100
            
            return 100.0 if attempt.passed else 0.0
        
        # Récupérer les données pour chaque jour du mois
        daily_data = []
        current_date = first_day
        
        while current_date <= last_day:
            # Récupérer les tentatives pour ce jour
            attempts_for_date = TestAttempt.objects.filter(
                Q(completed_at__date=current_date, completed_at__isnull=False) |
                Q(started_at__date=current_date, completed_at__isnull=False)
            ).exclude(status='in_progress').distinct()
            
            # Séparer les tests initiaux et finaux
            initial_attempts = attempts_for_date.filter(etat='test_initial')
            final_attempts = attempts_for_date.filter(etat='test_final')
            
            # Calculer les moyennes
            initial_scores = []
            for attempt in initial_attempts:
                score = get_attempt_score(attempt)
                if score is not None and score >= 0:
                    initial_scores.append(score)
            
            final_scores = []
            for attempt in final_attempts:
                score = get_attempt_score(attempt)
                if score is not None and score >= 0:
                    final_scores.append(score)
            
            avg_initial = sum(initial_scores) / len(initial_scores) if initial_scores else 0.0
            avg_final = sum(final_scores) / len(final_scores) if final_scores else 0.0
            
            daily_data.append({
                "date": current_date.isoformat(),
                "day": current_date.day,
                "test_initial": round(avg_initial, 2),
                "test_final": round(avg_final, 2)
            })
            
            current_date += datetime.timedelta(days=1)
        
        return JsonResponse({
            "month": month,
            "year": year,
            "data": daily_data
        })
        
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur dans hse_stats_monthly: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            "error": f"Erreur serveur: {str(e)}"
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
