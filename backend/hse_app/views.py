# hse_app/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg, F
from django.core.paginator import Paginator
import json
from datetime import datetime, timedelta
from tests.models import Test, Question, TestAttempt
from hse_app.models import HSEManager, HSEUser
from authentication.models import TestUser


# ==================== API HSE USERS (Participants) ====================

@csrf_exempt
def search_hse_user_by_cin(request):
    """
    Rechercher un utilisateur HSE par CIN
    GET: /api/hse/users/search/?cin=AB123456
    Note: Pas de @login_required car utilisé pour vérifier le CIN avant authentification
    """
    cin_raw = request.GET.get('cin', '').strip()
    
    if not cin_raw:
        return JsonResponse({
            'success': False,
            'error': 'CIN requis'
        }, status=400)
    
    # Log pour débogage
    import logging
    import sys
    logger = logging.getLogger(__name__)
    
    # Normaliser le CIN de la requête (majuscules, supprimer espaces, tirets, underscores)
    cin = cin_raw.upper()
    cin_normalized = cin.replace(' ', '').replace('-', '').replace('_', '').strip()
    
    # Logger dans stdout pour voir dans docker logs
    print(f"[CIN SEARCH] Recherche CIN: original='{cin_raw}' -> majuscules='{cin}' -> normalisé='{cin_normalized}'", file=sys.stderr)
    logger.info(f"Recherche CIN: original='{cin_raw}' -> majuscules='{cin}' -> normalisé='{cin_normalized}'")
    
    try:
        # Essayer d'abord recherche exacte insensible à la casse
        user = None
        try:
            user = HSEUser.objects.get(cin__iexact=cin_normalized)
            print(f"[CIN SEARCH] ✓ Trouvé avec iexact: {user.cin}", file=sys.stderr)
            logger.info(f"CIN trouvé avec recherche exacte: {user.cin}")
        except HSEUser.DoesNotExist:
            # Si pas trouvé, essayer avec recherche qui ignore les espaces dans la base
            print(f"[CIN SEARCH] ✗ Non trouvé avec iexact, recherche dans tous les utilisateurs...", file=sys.stderr)
            logger.info(f"CIN non trouvé avec recherche exacte, recherche dans tous les utilisateurs...")
            
            # Essayer aussi avec le CIN original (sans normalisation)
            try:
                user = HSEUser.objects.get(cin__iexact=cin)
                print(f"[CIN SEARCH] ✓ Trouvé avec iexact (original): {user.cin}", file=sys.stderr)
                logger.info(f"CIN trouvé avec recherche exacte (original): {user.cin}")
            except HSEUser.DoesNotExist:
                # Chercher tous les utilisateurs et comparer manuellement
                all_users = HSEUser.objects.all()
                user_count = all_users.count()
                print(f"[CIN SEARCH] Parcours de {user_count} utilisateurs...", file=sys.stderr)
                
                for u in all_users:
                    # Normaliser le CIN de la base de données
                    db_cin = str(u.cin)
                    db_cin_normalized = db_cin.replace(' ', '').replace('-', '').replace('_', '').strip().upper()
                    
                    # Comparer avec le CIN normalisé de la requête
                    if db_cin_normalized == cin_normalized:
                        user = u
                        print(f"[CIN SEARCH] ✓ Trouvé avec normalisation: {u.cin} (recherché: {cin_normalized})", file=sys.stderr)
                        logger.info(f"CIN trouvé avec recherche normalisée: {u.cin} (recherché: {cin_normalized})")
                        break
                
                if not user:
                    # Log tous les CIN disponibles pour débogage
                    all_cins = [str(u.cin) for u in HSEUser.objects.all()[:10]]  # Limiter à 10 pour le log
                    print(f"[CIN SEARCH] ✗ CIN non trouvé. Recherché: '{cin_normalized}'. Exemples: {all_cins}", file=sys.stderr)
                    logger.warning(f"CIN non trouvé. CIN recherché: '{cin_normalized}'. Exemples de CIN en base: {all_cins}")
                    raise HSEUser.DoesNotExist
        
        # Récupérer les tentatives de test (optionnel, seulement si authentifié)
        attempts_data = []
        attempts_count = 0
        if request.user.is_authenticated:
            attempts = TestAttempt.objects.filter(user__cin=cin).order_by('-started_at')
            attempts_count = attempts.count()
            for attempt in attempts[:5]:  # 5 dernières tentatives
                attempts_data.append({
                    'test_version': attempt.test.version,
                    'started_at': attempt.started_at.isoformat() if attempt.started_at else None,
                    'status': attempt.status,
                    'passed': attempt.passed,
                    'total_score': attempt.overall_score_percentage,
                    'mandatory_score': attempt.mandatory_score_percentage,
                    'langue': attempt.get_langue_display()
                })
        
        user_data = {
            'id': user.id,
            'nom': user.nom,
            'prenom': user.prénom,
            'full_name': user.get_full_name(),
            'cin': user.cin,
            'entite': user.entite,
            'entreprise': user.entreprise,
            'chef_projet_ocp': user.chef_projet_ocp,
            'presence': user.presence,
            'sensibilise_avec_succes': user.sensibilise_avec_succes,
            'taux_reussite': user.taux_reussite,
            'recent_attempts': attempts_data,
            'attempts_count': attempts_count
        }
        
        return JsonResponse({
            'success': True,
            'user': user_data,
            'message': 'Utilisateur HSE trouvé'
        })
        
    except HSEUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Aucun utilisateur HSE trouvé avec ce CIN'
        }, status=404)


@csrf_exempt
@login_required
def create_hse_user(request):
    """
    Créer un nouvel utilisateur HSE
    POST: /api/hse/users/create/
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Accès non autorisé'
        }, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Vérifier si le CIN existe déjà
            cin = data.get('cin', '').strip().upper()
            if HSEUser.objects.filter(cin=cin).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Un utilisateur avec le CIN {cin} existe déjà'
                }, status=400)
            
            # Créer l'utilisateur
            user = HSEUser.objects.create(
                nom=data['nom'],
                prénom=data.get('prenom', data.get('prénom', '')),
                cin=cin,
                entite=data.get('entite', ''),
                entreprise=data.get('entreprise', ''),
                chef_projet_ocp=data.get('chef_projet_ocp', ''),
                presence=data.get('presence', False)
            )
            
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'full_name': user.get_full_name(),
                    'cin': user.cin,
                    'entreprise': user.entreprise,
                    'entite': user.entite
                },
                'message': 'Utilisateur HSE créé avec succès'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Format JSON invalide'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur création: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Méthode non autorisée'
    }, status=405)


@csrf_exempt
def list_hse_users(request):
    """
    Lister les utilisateurs HSE avec pagination et filtres
    GET: /api/hse/users/?search=...&entreprise=...&page=1&date_ajout=2025-12-13
    """
    # Permettre l'accès sans authentification pour l'affichage
    
    # Filtres
    search = request.GET.get('search', '')
    entreprise = request.GET.get('entreprise', '')
    entite = request.GET.get('entite', '')
    presence = request.GET.get('presence')
    date_ajout = request.GET.get('date_ajout', '')
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # Construction de la requête
    users = HSEUser.objects.all()
    
    if search:
        users = users.filter(
            Q(nom__icontains=search) |
            Q(prénom__icontains=search) |
            Q(cin__icontains=search) |
            Q(email__icontains=search)
        )
    
    if entreprise:
        users = users.filter(entreprise__icontains=entreprise)
    
    if entite:
        users = users.filter(entite__icontains=entite)
    
    if presence is not None:
        users = users.filter(presence=(presence.lower() == 'true'))
    
    # Filtrer par date d'ajout
    if date_ajout:
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_ajout, '%Y-%m-%d').date()
            users = users.filter(date_ajout=date_obj)
            # Debug: compter les résultats
            count = users.count()
        except ValueError as e:
            # Si la date est invalide, on ignore le filtre
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur parsing date: {e}")
            pass
    
    # Pagination
    paginator = Paginator(users.order_by('nom', 'prénom'), page_size)
    page_obj = paginator.get_page(page)
    
    users_data = []
    for user in page_obj:
        try:
            # Calculer taux_reussite de manière sécurisée
            taux_reussite = 0
            try:
                taux_reussite = user.taux_reussite
            except Exception as e:
                # Si erreur lors du calcul du taux_reussite, mettre à 0
                taux_reussite = 0
            
            # Récupérer date_ajout de manière sécurisée
            date_ajout_str = None
            try:
                if hasattr(user, 'date_ajout') and user.date_ajout:
                    date_ajout_str = user.date_ajout.isoformat()
            except Exception:
                pass
            
            users_data.append({
                'id': user.id,
                'cin': user.cin,
                'nom': user.nom,
                'prenom': user.prénom,
                'full_name': user.get_full_name(),
                'entreprise': user.entreprise,
                'entite': user.entite,
                'chef_projet_ocp': user.chef_projet_ocp or '',
                'presence': user.presence,
                'sensibilise_avec_succes': user.sensibilise_avec_succes,
                'taux_reussite': taux_reussite,
                'test_attempts': TestAttempt.objects.filter(user__cin=user.cin).count(),
                'date_ajout': date_ajout_str
            })
        except Exception as e:
            # Logger l'erreur mais continuer avec les autres utilisateurs
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de la sérialisation de l'utilisateur {user.id}: {str(e)}")
            continue
    
    try:
        return JsonResponse({
            'success': True,
            'users': users_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': paginator.count,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur dans list_hse_users: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': f'Erreur serveur: {str(e)}',
            'users': []
        }, status=500)


# ==================== API HSE TESTS ====================

def list_hse_tests(request):
    """
    Lister tous les tests HSE disponibles
    GET: /api/hse/tests/
    """
    tests = Test.objects.filter(is_active=True).order_by('version')
    
    tests_data = []
    for test in tests:
        tests_data.append({
            'id': test.id,
            'version': test.version,
            'description': test.description,
            'duration_minutes': test.duration_minutes,
            'total_questions': test.total_questions,
            'mandatory_questions_count': test.mandatory_questions_count,
            'optional_questions_count': test.optional_questions_count,
            'passing_score_optional': test.passing_score_optional,
            'is_active': test.is_active,
            'questions_in_order': test.ordre_questions,
            'mandatory_questions': test.mandatory_questions
        })
    
    return JsonResponse({
        'success': True,
        'tests': tests_data,
        'count': len(tests_data)
    })


def get_hse_test_details(request, version):
    """Détails d'un test HSE spécifique"""
    try:
        test = Test.objects.get(version=version, is_active=True)
        # ... ta logique pour retourner les détails du test
    except Test.DoesNotExist:
        return JsonResponse({'success': False, 'error': f'Test version {version} non trouvé'})


@csrf_exempt
@login_required
def submit_hse_test_answers(request, attempt_id):
    """
    Soumettre les réponses d'un test HSE
    POST: /api/hse/test-attempts/{attempt_id}/submit/
    {
        "answers": {
            "1": true,  # ← true/false directement
            "2": false,
            "3": true,
            ...
        }
    }
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        user_answers = data.get('answers', {})
        
        # Récupérer la tentative
        attempt = TestAttempt.objects.get(
            id=attempt_id,
            user=request.user,
            status='in_progress'
        )
        
        # Mettre à jour les réponses (format simplifié)
        attempt.user_answers = user_answers
        attempt.completed_at = datetime.now()
        
        # Calculer le temps pris
        if attempt.started_at and attempt.completed_at:
            time_taken = attempt.completed_at - attempt.started_at
            attempt.time_taken_seconds = int(time_taken.total_seconds())
        
        # Calculer les scores
        test = attempt.test
        # Utiliser mandatory_questions du test si disponible, sinon utiliser is_mandatory des questions
        mandatory_ids = set(test.mandatory_questions) if test.mandatory_questions else set()
        
        mandatory_correct = 0
        optional_correct = 0
        
        for question_id_str, user_answer in user_answers.items():
            try:
                question_id = int(question_id_str)
                question = Question.objects.get(id=question_id)
            except (ValueError, Question.DoesNotExist):
                continue
            
            # Normaliser la réponse en booléen si nécessaire
            # Gérer les cas où la réponse arrive comme chaîne "true"/"false" ou entier 1/0
            if isinstance(user_answer, dict):
                user_answer = user_answer.get('answer')
            
            if isinstance(user_answer, str):
                user_answer = user_answer.lower().strip()
                # Gérer les réponses en français, anglais et arabe
                if user_answer in ['true', 'vrai', '1', 'yes', 'oui', 't', 'نعم']:
                    user_answer = True
                elif user_answer in ['false', 'faux', '0', 'no', 'non', 'f', 'لا']:
                    user_answer = False
                else:
                    continue  # Réponse invalide, passer à la suivante
            elif isinstance(user_answer, int):
                user_answer = bool(user_answer)
            elif user_answer is None:
                continue  # Pas de réponse, passer à la suivante
            
            # Vérifier la réponse en utilisant la fonction check_answer du modèle
            is_correct = question.check_answer(user_answer)
            
            # Déterminer si la question est obligatoire :
            # 1. Si elle est dans mandatory_questions du test
            # 2. Sinon, si is_mandatory de la question est True
            is_mandatory_question = question_id in mandatory_ids or question.is_mandatory
                
            if is_mandatory_question:
                if is_correct:
                    mandatory_correct += 1
            else:
                if is_correct:
                    optional_correct += 1
                                    
        # Calculer le total des questions obligatoires
        total_mandatory = len(mandatory_ids) if mandatory_ids else 0
        if total_mandatory == 0:
            # Si aucune question n'est marquée comme obligatoire dans le test,
            # compter celles avec is_mandatory=True
            for question_id_str in user_answers.keys():
                try:
                    question_id = int(question_id_str)
                    question = Question.objects.get(id=question_id)
                    if question.is_mandatory:
                        total_mandatory += 1
                except (Question.DoesNotExist, ValueError):
                    continue
        
        # Mettre à jour les scores
        attempt.mandatory_correct = mandatory_correct
        attempt.mandatory_wrong = total_mandatory - mandatory_correct
        attempt.mandatory_total = total_mandatory
        attempt.optional_correct = optional_correct
        attempt.optional_wrong = test.total_questions - total_mandatory - optional_correct
        attempt.optional_total = test.total_questions - total_mandatory
        attempt.mandatory_score_percentage = round((mandatory_correct / total_mandatory * 100), 2) if total_mandatory > 0 else 0
        attempt.optional_score_percentage = round((optional_correct / attempt.optional_total * 100), 2) if attempt.optional_total > 0 else 0
        attempt.overall_score_percentage = round(((mandatory_correct + optional_correct) / test.total_questions * 100), 2) if test.total_questions > 0 else 0
        attempt.passed = mandatory_correct == total_mandatory if total_mandatory > 0 else False
        attempt.status = 'passed' if attempt.passed else 'failed'
        
        attempt.save()
        
        # Mettre à jour sensibilise_avec_succes si le test est réussi
        if attempt.passed:
            try:
                # Trouver l'utilisateur HSE correspondant via le CIN
                hse_user = HSEUser.objects.get(cin=attempt.user.cin)
                hse_user.sensibilise_avec_succes = True
                hse_user.save(update_fields=['sensibilise_avec_succes'])
            except HSEUser.DoesNotExist:
                # L'utilisateur HSE n'existe pas encore, ce n'est pas grave
                pass
            except Exception as e:
                # Logger l'erreur mais ne pas bloquer la soumission du test
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Erreur lors de la mise à jour de sensibilise_avec_succes: {str(e)}")
        
        # Note: Le champ 'presence' n'est pas mis à jour automatiquement
        # Il doit être géré manuellement par un manager
            
        return JsonResponse({
            'success': True,
            'results': {
                'passed': attempt.passed,
                'mandatory': {
                    'correct': mandatory_correct,
                    'total': len(mandatory_ids),
                    'percentage': attempt.mandatory_score_percentage,
                    'passed': mandatory_correct == len(mandatory_ids)
                },
                'optional': {
                    'correct': optional_correct,
                    'total': attempt.optional_total,
                    'percentage': attempt.optional_score_percentage
                },
                'overall': {
                    'correct': mandatory_correct + optional_correct,
                    'total': test.total_questions,
                    'percentage': attempt.overall_score_percentage
                },
                'time_taken_seconds': attempt.time_taken_seconds
            },
            'message': 'Test soumis avec succès'
        })
            
    return JsonResponse({
        'success': False,
        'error': 'Méthode non autorisée'
    }, status=405)


# ==================== API TEST ATTEMPTS ====================

@csrf_exempt
@login_required
def start_hse_test_attempt(request):
    """
    Démarrer une tentative de test HSE
    POST: /api/hse/test-attempts/start/
    {
        "test_version": 1,
        "langue": "fr"
    }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            test_version = data.get('test_version')
            langue = data.get('langue', 'ar')
            
            # Vérifier l'utilisateur
            user = request.user
            
            # Récupérer le test
            try:
                test = Test.objects.get(version=test_version, is_active=True)
            except Test.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Test version {test_version} non trouvé'
                }, status=404)
            
            # Vérifier si une tentative existe déjà
            existing_attempt = TestAttempt.objects.filter(
                user=user,
                test=test,
                status='in_progress'
            ).first()
            
            if existing_attempt:
                # Retourner la tentative existante
                return JsonResponse({
                    'success': True,
                    'attempt_id': existing_attempt.id,
                    'test_version': test.version,
                    'started_at': existing_attempt.started_at.isoformat(),
                    'message': 'Tentative en cours trouvée'
                })
            
            # Créer une nouvelle tentative
            attempt = TestAttempt.objects.create(
                test=test,
                user=user,
                langue=langue,
                status='in_progress',
                started_at=datetime.now()
            )
            
            # Récupérer les questions dans l'ordre
            questions_in_order = test.get_questions_in_order()
            
            questions_data = []
            for question in questions_in_order:
                is_mandatory = str(question.id) in [str(qid) for qid in test.mandatory_questions]
                
                # Pour le test, on ne montre pas la réponse correcte
                # Construire l'URL complète de l'image
                image_url = None
                if question.image:
                    image_url = request.build_absolute_uri(question.image.url)
                
                question_display = {
                    'id': question.id,
                    'question_code': question.question_code,
                    'enonce': question.get_enonce(langue),
                    'is_mandatory': is_mandatory,
                    'points': question.points,
                    'has_image': question.has_image,
                    'image_url': image_url
                }
                questions_data.append(question_display)
            
            return JsonResponse({
                'success': True,
                'attempt': {
                    'id': attempt.id,
                    'test_version': test.version,
                    'langue': attempt.get_langue_display(),
                    'started_at': attempt.started_at.isoformat(),
                    'duration_minutes': test.duration_minutes,
                    'total_questions': test.total_questions,
                    'mandatory_count': test.mandatory_questions_count
                },
                'questions': questions_data,
                'message': 'Test démarré avec succès'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Format JSON invalide'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Méthode non autorisée'
    }, status=405)


@login_required
def get_user_test_history(request):
    """
    Historique des tests passés par l'utilisateur
    GET: /api/hse/test-attempts/history/
    """
    user = request.user
    
    attempts = TestAttempt.objects.filter(
        user=user,
        completed_at__isnull=False
    ).order_by('-started_at')
    
    history = []
    for attempt in attempts:
        history.append({
            'id': attempt.id,
            'test_version': attempt.test.version,
            'test_description': attempt.test.description,
            'started_at': attempt.started_at.isoformat() if attempt.started_at else None,
            'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
            'langue': attempt.get_langue_display(),
            'status': attempt.status,
            'passed': attempt.passed,
            'scores': {
                'mandatory': f"{attempt.mandatory_correct}/{attempt.mandatory_total}",
                'optional': f"{attempt.optional_correct}/{attempt.optional_total}",
                'overall': f"{round(attempt.overall_score_percentage)}%"
            },
            'time_taken': f"{attempt.time_taken_seconds // 60}:{attempt.time_taken_seconds % 60:02d}"
        })
    
    return JsonResponse({
        'success': True,
        'history': history,
        'count': len(history)
    })


# ==================== API STATISTIQUES HSE ====================

@login_required
def get_hse_statistics(request):
    """
    Statistiques HSE globales
    GET: /api/hse/statistics/
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Accès non autorisé'
        }, status=403)
    
    # Statistiques utilisateurs
    total_users = HSEUser.objects.count()
    users_present = HSEUser.objects.filter(presence=True).count()
    
    # Statistiques tests
    total_attempts = TestAttempt.objects.count()
    completed_attempts = TestAttempt.objects.filter(completed_at__isnull=False).count()
    passed_attempts = TestAttempt.objects.filter(passed=True).count()
    
    # Taux de réussite
    success_rate = (passed_attempts / completed_attempts * 100) if completed_attempts > 0 else 0
    
    # Répartition par version de test
    attempts_by_version = TestAttempt.objects.values('test__version').annotate(
        count=Count('id'),
        avg_score=Avg('overall_score_percentage'),
        passed_count=Count('id', filter=Q(passed=True))
    ).order_by('test__version')
    
    version_stats = []
    for stat in attempts_by_version:
        version_stats.append({
            'version': stat['test__version'],
            'attempts': stat['count'],
            'avg_score': round(stat['avg_score'], 2) if stat['avg_score'] else 0,
            'passed': stat['passed_count'],
            'pass_rate': round((stat['passed_count'] / stat['count'] * 100), 2) if stat['count'] > 0 else 0
        })
    
    # Répartition par langue
    attempts_by_langue = TestAttempt.objects.values('langue').annotate(
        count=Count('id'),
        avg_score=Avg('overall_score_percentage')
    )
    
    langue_stats = []
    for stat in attempts_by_langue:
        langue_stats.append({
            'langue': dict(TestAttempt._meta.get_field('langue').choices).get(stat['langue'], stat['langue']),
            'attempts': stat['count'],
            'avg_score': round(stat['avg_score'], 2) if stat['avg_score'] else 0
        })
    
    # Meilleurs scores
    top_scores = TestAttempt.objects.filter(
        completed_at__isnull=False
    ).select_related('user', 'test').order_by('-overall_score_percentage')[:10]
    
    top_scores_data = []
    for attempt in top_scores:
        top_scores_data.append({
            'user_name': attempt.user.get_full_name(),
            'user_cin': attempt.user.cin,
            'test_version': attempt.test.version,
            'score': round(attempt.overall_score_percentage, 2),
            'passed': attempt.passed,
            'completed_at': attempt.completed_at.date().isoformat() if attempt.completed_at else None
        })
    
    return JsonResponse({
        'success': True,
        'statistics': {
            'users': {
                'total': total_users,
                'present': users_present,
                'present_percentage': round((users_present / total_users * 100), 2) if total_users > 0 else 0,
                'absent': total_users - users_present,
                'absent_percentage': round(((total_users - users_present) / total_users * 100), 2) if total_users > 0 else 0
            },
            'attempts': {
                'total': total_attempts,
                'completed': completed_attempts,
                'passed': passed_attempts,
                'completion_rate': round((completed_attempts / total_attempts * 100), 2) if total_attempts > 0 else 0,
                'success_rate': round(success_rate, 2)
            },
            'by_version': version_stats,
            'by_langue': langue_stats,
            'top_scores': top_scores_data
        },
        'as_of_date': datetime.now().date().isoformat()
    })


# ==================== API HSE MANAGERS ====================

@login_required
def list_hse_managers(request):
    """
    Lister les managers HSE
    GET: /api/hse/managers/
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Accès non autorisé'
        }, status=403)
    
    managers = HSEManager.objects.all().order_by('full_name')
    
    managers_data = []
    for manager in managers:
        managers_data.append({
            'id': manager.id,
            'full_name': manager.full_name,
            'cin': manager.cin,
        })
    
    return JsonResponse({
        'success': True,
        'managers': managers_data,
        'count': len(managers_data)
    })


@csrf_exempt
@login_required
def create_hse_manager(request):
    """
    Créer un nouveau manager HSE
    POST: /api/hse/managers/create/
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Accès non autorisé'
        }, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            manager = HSEManager.objects.create(
                name=data['name'],
                cin=data.get('cin', '')
            )
            
            return JsonResponse({
                'success': True,
                'manager': {
                    'id': manager.id,
                    'name': manager.name,
                    'cin': manager.cin
                },
                'message': 'Manager HSE créé avec succès'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur création: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Méthode non autorisée'
    }, status=405)


# ==================== API SYNCHRONISATION ====================

@login_required
def sync_test_users_with_hse(request):
    """
    Synchroniser les TestUsers avec les HSEUsers
    GET: /api/hse/sync-users/
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Accès non autorisé'
        }, status=403)
    
    try:
        synced = 0
        created = 0
        errors = []
        
        # Récupérer tous les TestUsers qui n'ont pas de HSEUser correspondant
        test_users = TestUser.objects.all()
        
        for test_user in test_users:
            try:
                # Vérifier si HSEUser existe déjà
                hse_user, created_flag = HSEUser.objects.get_or_create(
                    cin=test_user.cin,
                    defaults={
                        'nom': test_user.last_name or '',
                        'prénom': test_user.first_name or test_user.username,
                        'entite': 'Non spécifié',
                        'entreprise': 'Non spécifié'
                    }
                )
                
                # Mettre à jour les informations si nécessaire
                if not created_flag:
                    if test_user.first_name and not hse_user.prénom:
                        hse_user.prénom = test_user.first_name
                    if test_user.last_name and not hse_user.nom:
                        hse_user.nom = test_user.last_name
                    hse_user.save()
                    synced += 1
                else:
                    created += 1
                    
            except Exception as e:
                errors.append({
                    'user_cin': test_user.cin,
                    'error': str(e)
                })
        
        return JsonResponse({
            'success': True,
            'sync_result': {
                'test_users_processed': test_users.count(),
                'hse_users_created': created,
                'hse_users_updated': synced,
                'errors_count': len(errors)
            },
            'message': f'Synchronisation terminée: {created} créés, {synced} mis à jour'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur synchronisation: {str(e)}'
        }, status=500)


# ==================== API IMPORT EXCEL ====================

@csrf_exempt
# @login_required  # Temporairement désactivé
def preview_hse_users_excel(request):
    """
    Prévisualiser les données d'un fichier Excel sans les importer
    POST: /api/users/import/preview/
    Content-Type: multipart/form-data
    file: fichier Excel (.xlsx, .xls)
    
    NOTE: Cette fonction utilise la fonction unifiée upload_excel de views_api
    """
    # Utiliser directement la fonction unifiée
    from .views_api import upload_excel
    from rest_framework.request import Request
    from rest_framework.response import Response as DRFResponse
    
    # Convertir la requête Django en requête DRF
    drf_request = Request(request)
    drf_response = upload_excel(drf_request)
    
    # Convertir la réponse DRF en JsonResponse Django
    if hasattr(drf_response, 'data'):
        return JsonResponse(drf_response.data, status=drf_response.status_code)
    return JsonResponse({'success': False, 'error': 'Erreur de conversion'}, status=500)


@csrf_exempt
# @login_required  # Temporairement désactivé pour permettre l'import sans auth
def import_hse_users(request):
    """
    Importer des utilisateurs HSE depuis un fichier Excel
    POST: /api/users/import/
    Content-Type: multipart/form-data
    file: fichier Excel (.xlsx, .xls)
    """
    # Temporairement désactivé pour permettre l'import sans auth
    # if not request.user.is_staff:
    #     return JsonResponse({
    #         'success': False,
    #         'error': 'Accès non autorisé'
    #     }, status=403)
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Méthode non autorisée'
        }, status=405)
    
    if 'file' not in request.FILES:
        return JsonResponse({
            'success': False,
            'error': 'Aucun fichier fourni'
        }, status=400)
    
    excel_file = request.FILES['file']
    
    # Vérifier l'extension
    if not excel_file.name.endswith(('.xlsx', '.xls')):
        return JsonResponse({
            'success': False,
            'error': 'Le fichier doit être au format Excel (.xlsx ou .xls)'
        }, status=400)
    
    try:
        from .import_excel import import_hse_users_excel
        result = import_hse_users_excel(excel_file)
        
        if result['status'] == 'error':
            return JsonResponse({
                'success': False,
                'error': result.get('message', 'Erreur lors de l\'import')
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'message': f'Import réussi : {result["created"]} créés, {result["updated"]} mis à jour',
            'summary': {
                'created': result['created'],
                'updated': result['updated'],
                'total_processed': result.get('total_processed', 0),
                'errors_count': len(result.get('errors', []))
            },
            'errors': result.get('errors', []),
            'data': result.get('data', [])  # Retourner les données du fichier Excel
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de l\'import : {str(e)}'
        }, status=500)


# ==================== API MODIFICATION DE PRÉSENCE ====================

@csrf_exempt
def update_user_presence(request, user_id):
    """
    Modifier la présence d'un utilisateur HSE
    PATCH: /api/hse/users/{user_id}/presence/
    {
        "presence": true
    }
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Log de la requête entrante
    logger.info(f"update_user_presence appelé - Method: {request.method}, User ID: {user_id}, Body: {request.body}")
    print(f"[DEBUG] update_user_presence - Method: {request.method}, User ID: {user_id}")
    
    # Accepter PATCH, POST et PUT pour compatibilité
    if request.method not in ['PATCH', 'POST', 'PUT']:
        logger.warning(f"Méthode non autorisée: {request.method}")
        return JsonResponse({
            'success': False,
            'error': f'Méthode non autorisée: {request.method}. Utilisez PATCH, POST ou PUT.'
        }, status=405)
    
    # Pour POST et PUT, traiter comme PATCH
    if request.method in ['POST', 'PUT']:
        logger.info(f"Méthode {request.method} acceptée, traitement comme PATCH")
    
    try:
        user = HSEUser.objects.get(id=user_id)
        logger.info(f"Utilisateur trouvé: {user.cin}, présence actuelle: {user.presence}")
        print(f"[DEBUG] Utilisateur trouvé: {user.cin}, présence actuelle: {user.presence}")
        
        try:
            data = json.loads(request.body)
            logger.info(f"Données parsées: {data}")
            print(f"[DEBUG] Données parsées: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON: {str(e)}, Body: {request.body}")
            return JsonResponse({
                'success': False,
                'error': f'Format JSON invalide: {str(e)}'
            }, status=400)
        
        if 'presence' in data:
            old_presence = user.presence
            new_presence = bool(data.get('presence', False))
            logger.info(f"Changement de présence: {old_presence} -> {new_presence}")
            print(f"[DEBUG] Changement de présence: {old_presence} -> {new_presence}")
            
            # Utiliser une transaction pour garantir la cohérence
            from django.db import transaction
            
            with transaction.atomic():
                # Méthode 1: Utiliser update() directement pour forcer la mise à jour en base
                rows_updated = HSEUser.objects.filter(id=user_id).update(presence=new_presence)
                logger.info(f"Update direct effectué: {rows_updated} ligne(s) mise(s) à jour")
                print(f"[DEBUG] Update direct effectué: {rows_updated} ligne(s) mise(s) à jour")
                
                if rows_updated == 0:
                    logger.warning(f"Aucune ligne mise à jour avec update(), essai avec save()")
                    print(f"[WARNING] Aucune ligne mise à jour avec update(), essai avec save()")
                    user.presence = new_presence
                    user.save(update_fields=['presence'])
                    rows_updated = 1
                
                # Vérifier directement dans la base avec une nouvelle requête
                # pour s'assurer que la valeur est bien persistée
                user_from_db = HSEUser.objects.get(id=user_id)
                logger.info(f"Vérification directe DB (dans transaction), présence: {user_from_db.presence}")
                print(f"[DEBUG] Vérification directe DB (dans transaction), présence: {user_from_db.presence}")
                
                # S'assurer que la valeur est correcte
                if user_from_db.presence != new_presence:
                    logger.error(f"ERREUR: La présence n'a pas été mise à jour! Attendu: {new_presence}, Obtenu: {user_from_db.presence}")
                    print(f"[ERROR] ERREUR: La présence n'a pas été mise à jour! Attendu: {new_presence}, Obtenu: {user_from_db.presence}")
                    # Essayer une dernière fois avec save()
                    user_from_db.presence = new_presence
                    user_from_db.save(update_fields=['presence'])
                    user_from_db.refresh_from_db()
                    logger.info(f"Après save() final, présence: {user_from_db.presence}")
                    print(f"[DEBUG] Après save() final, présence: {user_from_db.presence}")
            
            # Recharger une dernière fois après la transaction pour confirmation finale
            user_from_db = HSEUser.objects.get(id=user_id)
            final_presence = user_from_db.presence
            logger.info(f"Valeur finale confirmée (après transaction): {final_presence}")
            print(f"[DEBUG] Valeur finale confirmée (après transaction): {final_presence}")
            
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user_from_db.id,
                    'cin': user_from_db.cin,
                    'full_name': user_from_db.get_full_name(),
                    'presence': final_presence
                },
                'message': f'Présence mise à jour de {old_presence} à {final_presence}',
                'debug': {
                    'old_presence': old_presence,
                    'new_presence': new_presence,
                    'final_presence': final_presence,
                    'rows_updated': rows_updated
                }
            })
        else:
            logger.warning(f"Champ 'presence' manquant dans les données: {data}")
            return JsonResponse({
                'success': False,
                'error': 'Champ "presence" manquant dans la requête',
                'received_data': data
            }, status=400)
    
    except HSEUser.DoesNotExist:
        logger.error(f"Utilisateur avec ID {user_id} non trouvé")
        return JsonResponse({
            'success': False,
            'error': f'Utilisateur avec ID {user_id} non trouvé'
        }, status=404)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Erreur dans update_user_presence: {str(e)}\n{error_trace}")
        print(f"[ERROR] {str(e)}\n{error_trace}")
        return JsonResponse({
            'success': False,
            'error': f'Erreur: {str(e)}',
            'traceback': error_trace
        }, status=500)


# ==================== API MODIFICATION DE SENSIBILISATION ====================

@csrf_exempt
def update_user_sensibilise(request, user_id):
    """
    Modifier la sensibilisation d'un utilisateur HSE
    PATCH: /api/hse/users/{user_id}/sensibilise/
    {
        "sensibilise_avec_succes": true
    }
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"update_user_sensibilise appelé - Method: {request.method}, User ID: {user_id}")
    
    if request.method not in ['PATCH', 'POST', 'PUT']:
        return JsonResponse({
            'success': False,
            'error': f'Méthode non autorisée: {request.method}. Utilisez PATCH, POST ou PUT.'
        }, status=405)
    
    try:
        user = HSEUser.objects.get(id=user_id)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error': f'Format JSON invalide: {str(e)}'
            }, status=400)
        
        if 'sensibilise_avec_succes' in data:
            old_sensibilise = user.sensibilise_avec_succes
            new_sensibilise = bool(data.get('sensibilise_avec_succes', False))
            
            from django.db import transaction
            with transaction.atomic():
                rows_updated = HSEUser.objects.filter(id=user_id).update(sensibilise_avec_succes=new_sensibilise)
                if rows_updated == 0:
                    user.sensibilise_avec_succes = new_sensibilise
                    user.save(update_fields=['sensibilise_avec_succes'])
            
            user_from_db = HSEUser.objects.get(id=user_id)
            final_sensibilise = user_from_db.sensibilise_avec_succes
            
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user_from_db.id,
                    'cin': user_from_db.cin,
                    'full_name': user_from_db.get_full_name(),
                    'sensibilise_avec_succes': final_sensibilise
                },
                'message': f'Sensibilisation mise à jour de {old_sensibilise} à {final_sensibilise}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Champ "sensibilise_avec_succes" manquant dans la requête'
            }, status=400)
    
    except HSEUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Utilisateur avec ID {user_id} non trouvé'
        }, status=404)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Erreur dans update_user_sensibilise: {str(e)}\n{error_trace}")
        return JsonResponse({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }, status=500)


# ==================== API SUPPRESSION UTILISATEUR ====================

@csrf_exempt
def delete_hse_user(request, user_id):
    """
    Supprimer un utilisateur HSE
    DELETE: /api/hse/users/{user_id}/delete/
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"delete_hse_user appelé - Method: {request.method}, User ID: {user_id}")
    print(f"[DEBUG] delete_hse_user - Method: {request.method}, User ID: {user_id}")
    
    # Accepter DELETE et POST pour compatibilité
    if request.method not in ['DELETE', 'POST']:
        return JsonResponse({
            'success': False,
            'error': f'Méthode non autorisée: {request.method}. Utilisez DELETE ou POST.'
        }, status=405)
    
    try:
        user = HSEUser.objects.get(id=user_id)
        user_cin = user.cin
        user_name = user.get_full_name()
        
        # Supprimer l'utilisateur
        user.delete()
        logger.info(f"Utilisateur supprimé: {user_cin} ({user_name})")
        print(f"[DEBUG] Utilisateur supprimé: {user_cin} ({user_name})")
        
        return JsonResponse({
            'success': True,
            'message': f'Utilisateur {user_name} (CIN: {user_cin}) supprimé avec succès',
            'deleted_user': {
                'id': user_id,
                'cin': user_cin,
                'name': user_name
            }
        })
    
    except HSEUser.DoesNotExist:
        logger.error(f"Utilisateur avec ID {user_id} non trouvé")
        return JsonResponse({
            'success': False,
            'error': f'Utilisateur avec ID {user_id} non trouvé'
        }, status=404)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Erreur dans delete_hse_user: {str(e)}\n{error_trace}")
        print(f"[ERROR] {str(e)}\n{error_trace}")
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la suppression: {str(e)}',
            'traceback': error_trace
        }, status=500)
