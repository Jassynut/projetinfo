# hse_app/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg, F
from django.core.paginator import Paginator
import json
from datetime import datetime, timedelta
from .models import HSEUser, HSETest, HSEQuestion, TestAttempt, HSEmanager
from authentication.models import TestUser


# ==================== API HSE USERS (Participants) ====================

@csrf_exempt
@login_required
def search_hse_user_by_cin(request):
    """
    Rechercher un utilisateur HSE par CIN
    GET: /api/hse/users/search/?cin=AB123456
    """
    cin = request.GET.get('cin', '').strip().upper()
    
    if not cin:
        return JsonResponse({
            'success': False,
            'error': 'CIN requis'
        }, status=400)
    
    try:
        user = HSEUser.objects.get(cin=cin)
        
        # Récupérer les tentatives de test
        attempts = TestAttempt.objects.filter(user__cin=cin).order_by('-started_at')
        attempts_data = []
        
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
            'email': user.email,
            'entite': user.entite,
            'entreprise': user.entreprise,
            'chef_projet_ocp': user.chef_projet_ocp,
            'presence': user.presence,
            'reussite': user.reussite,
            'score': user.score,
            'taux_reussite': user.taux_reussite,
            'recent_attempts': attempts_data,
            'attempts_count': attempts.count()
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
                email=data.get('email', ''),
                entite=data.get('entite', ''),
                entreprise=data.get('entreprise', ''),
                chef_projet_ocp=data.get('chef_projet_ocp', ''),
                presence=data.get('presence', False),
                reussite=data.get('reussite', False),
                score=data.get('score', 0)
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


@login_required
def list_hse_users(request):
    """
    Lister les utilisateurs HSE avec pagination et filtres
    GET: /api/hse/users/?search=...&entreprise=...&page=1
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Accès non autorisé'
        }, status=403)
    
    # Filtres
    search = request.GET.get('search', '')
    entreprise = request.GET.get('entreprise', '')
    entite = request.GET.get('entite', '')
    reussite = request.GET.get('reussite')
    
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
    
    if reussite is not None:
        users = users.filter(reussite=(reussite.lower() == 'true'))
    
    # Pagination
    paginator = Paginator(users.order_by('nom', 'prénom'), page_size)
    page_obj = paginator.get_page(page)
    
    users_data = []
    for user in page_obj:
        users_data.append({
            'id': user.id,
            'cin': user.cin,
            'nom': user.nom,
            'prenom': user.prénom,
            'full_name': user.get_full_name(),
            'email': user.email,
            'entreprise': user.entreprise,
            'entite': user.entite,
            'chef_projet_ocp': user.chef_projet_ocp,
            'presence': user.presence,
            'reussite': user.reussite,
            'score': user.score,
            'taux_reussite': user.taux_reussite,
            'test_attempts': TestAttempt.objects.filter(user__cin=user.cin).count()
        })
    
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


# ==================== API HSE TESTS ====================

def list_hse_tests(request):
    """
    Lister tous les tests HSE disponibles
    GET: /api/hse/tests/
    """
    tests = HSETest.objects.filter(is_active=True).order_by('version')
    
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
        mandatory_ids = set(test.mandatory_questions)
        
        mandatory_correct = 0
        optional_correct = 0
        
        for question_id_str, user_answer in user_answers.items():
            question_id = int(question_id_str)
            question = HSEQuestion.objects.get(id=question_id)
                
                # Vérifier la réponse (user_answer est déjà True/False)
            is_correct = question.check_answer(user_answer)
                
            if question_id in mandatory_ids:
                if is_correct:
                    mandatory_correct += 1
            else:
                if is_correct:
                    optional_correct += 1
                                    
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
                test = HSETest.objects.get(version=test_version, is_active=True)
            except HSETest.DoesNotExist:
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
                question_display = {
                    'id': question.id,
                    'question_code': question.question_code,
                    'enonce': question.get_enonce(langue),
                    'is_mandatory': is_mandatory,
                    'points': question.points,
                    'has_image': question.has_image,
                    'image_url': question.image.url if question.image else None
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


@csrf_exempt
@login_required
def submit_hse_test_answers(request, attempt_id):
    """
    Soumettre les réponses d'un test HSE
    POST: /api/hse/test-attempts/{attempt_id}/submit/
    {
        "answers": {
            "1": {"answer": true, "is_mandatory": true},
            "2": {"answer": false, "is_mandatory": false},
            ...
        }
    }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_answers = data.get('answers', {})
            
            # Récupérer la tentative
            attempt = TestAttempt.objects.get(
                id=attempt_id,
                user=request.user,
                status='in_progress'
            )
            
            # Mettre à jour les réponses
            attempt.user_answers = user_answers
            attempt.completed_at = datetime.now()
            
            # Calculer le temps pris
            if attempt.started_at and attempt.completed_at:
                time_taken = attempt.completed_at - attempt.started_at
                attempt.time_taken_seconds = int(time_taken.total_seconds())
            
            # Calculer les scores (version simple)
            test = attempt.test
            mandatory_ids = set(test.mandatory_questions)
            
            mandatory_correct = 0
            optional_correct = 0
            
            for question_id_str, answer_data in user_answers.items():
                try:
                    question_id = int(question_id_str)
                    question = HSEQuestion.objects.get(id=question_id)
                    
                    user_answer = answer_data.get('answer')
                    if user_answer is None:
                        continue
                    
                    # Vérifier la réponse
                    is_correct = question.check_answer(user_answer)
                    
                    if question_id in mandatory_ids:
                        if is_correct:
                            mandatory_correct += 1
                    else:
                        if is_correct:
                            optional_correct += 1
                            
                except (HSEQuestion.DoesNotExist, ValueError):
                    continue
            
            # Calculer les pourcentages
            total_mandatory = test.mandatory_questions_count
            total_optional = test.optional_questions_count
            
            mandatory_percentage = (mandatory_correct / total_mandatory * 100) if total_mandatory > 0 else 0
            optional_percentage = (optional_correct / total_optional * 100) if total_optional > 0 else 0
            total_questions = total_mandatory + total_optional
            total_correct = mandatory_correct + optional_correct
            overall_percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0
            
            # Déterminer si le test est réussi
            # Règle: Toutes les questions obligatoires doivent être correctes
            passed = mandatory_correct == total_mandatory
            
            # Mettre à jour les scores
            attempt.mandatory_correct = mandatory_correct
            attempt.mandatory_wrong = total_mandatory - mandatory_correct
            attempt.mandatory_total = total_mandatory
            attempt.optional_correct = optional_correct
            attempt.optional_wrong = total_optional - optional_correct
            attempt.optional_total = total_optional
            attempt.mandatory_score_percentage = round(mandatory_percentage, 2)
            attempt.optional_score_percentage = round(optional_percentage, 2)
            attempt.overall_score_percentage = round(overall_percentage, 2)
            attempt.passed = passed
            attempt.status = 'passed' if passed else 'failed'
            
            attempt.save()
            
            # Mettre à jour les statistiques de l'utilisateur HSE
            try:
                hse_user = HSEUser.objects.get(cin=request.user.cin)
                hse_user.score = round(overall_percentage)
                hse_user.reussite = passed
                hse_user.save()
            except HSEUser.DoesNotExist:
                # Créer un utilisateur HSE si non existant
                HSEUser.objects.create(
                    nom=request.user.last_name or '',
                    prénom=request.user.first_name or '',
                    cin=request.user.cin,
                    email=request.user.email or '',
                    entite='',
                    entreprise='',
                    score=round(overall_percentage),
                    reussite=passed,
                    presence=True
                )
            
            return JsonResponse({
                'success': True,
                'results': {
                    'passed': passed,
                    'mandatory': {
                        'correct': mandatory_correct,
                        'total': total_mandatory,
                        'percentage': round(mandatory_percentage, 2),
                        'passed': mandatory_correct == total_mandatory
                    },
                    'optional': {
                        'correct': optional_correct,
                        'total': total_optional,
                        'percentage': round(optional_percentage, 2)
                    },
                    'overall': {
                        'correct': total_correct,
                        'total': total_questions,
                        'percentage': round(overall_percentage, 2)
                    },
                    'time_taken_seconds': attempt.time_taken_seconds
                },
                'message': 'Test soumis avec succès'
            })
            
        except TestAttempt.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Tentative non trouvée'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur soumission: {str(e)}'
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
    users_reussite = HSEUser.objects.filter(reussite=True).count()
    
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
                'successful': users_reussite,
                'presence_rate': round((users_present / total_users * 100), 2) if total_users > 0 else 0,
                'success_rate': round((users_reussite / total_users * 100), 2) if total_users > 0 else 0
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
    
    managers = HSEmanager.objects.all().order_by('name')
    
    managers_data = []
    for manager in managers:
        managers_data.append({
            'id': manager.id,
            'name': manager.name,
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
            
            manager = HSEmanager.objects.create(
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
                        'email': test_user.email or '',
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
                    if test_user.email and not hse_user.email:
                        hse_user.email = test_user.email
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