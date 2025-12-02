# tests/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json
from .models import Test, TestSession, Question, Category
from datetime import timedelta

# ==================== API PUBLIC (tests disponibles) ====================

def list_available_tests(request):
    """Lister les tests disponibles"""
    tests = Test.objects.filter(is_active=True).order_by('-created_at')
    
    tests_data = []
    for test in tests:
        tests_data.append({
            'id': test.id,
            'title': test.title,
            'description': test.description,
            'category': test.category.name if test.category else 'Général',
            'duration_minutes': test.duration_minutes,
            'questions_count': test.questions_count,
            'difficulty': test.difficulty,
            'created_by': test.created_by.username if test.created_by else None,
            'created_at': test.created_at.isoformat() if test.created_at else None
        })
    
    return JsonResponse({
        'success': True,
        'tests': tests_data,
        'count': len(tests_data)
    })


def get_test_details(request, test_id):
    """Détails d'un test spécifique"""
    try:
        test = Test.objects.get(id=test_id, is_active=True)
        
        # Questions (sans les réponses correctes)
        questions = []
        for q in test.questions.all().order_by('order'):
            questions.append({
                'id': q.id,
                'text': q.text,
                'question_type': q.question_type,
                'order': q.order,
                'points': q.points,
                'options': [
                    {'id': opt.id, 'text': opt.text}
                    for opt in q.options.all()
                ] if hasattr(q, 'options') else []
            })
        
        return JsonResponse({
            'success': True,
            'test': {
                'id': test.id,
                'title': test.title,
                'description': test.description,
                'instructions': test.instructions,
                'duration_minutes': test.duration_minutes,
                'passing_score': test.passing_score,
                'category': test.category.name if test.category else 'Général',
                'questions_count': len(questions),
                'questions': questions
            }
        })
    except Test.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Test non trouvé'
        }, status=404)


# ==================== API MANAGER (création/gestion) ====================

@csrf_exempt
@login_required
def manager_create_test(request):
    """Créer un nouveau test (Manager seulement)"""
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Accès non autorisé'
        }, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            test = Test.objects.create(
                title=data['title'],
                description=data.get('description', ''),
                instructions=data.get('instructions', ''),
                duration_minutes=data.get('duration_minutes', 30),
                passing_score=data.get('passing_score', 70),
                difficulty=data.get('difficulty', 'medium'),
                is_active=data.get('is_active', True),
                created_by=request.user
            )
            
            # Assigner une catégorie si fournie
            if data.get('category_id'):
                try:
                    category = Category.objects.get(id=data['category_id'])
                    test.category = category
                    test.save()
                except Category.DoesNotExist:
                    pass
            
            return JsonResponse({
                'success': True,
                'test': {
                    'id': test.id,
                    'title': test.title,
                    'description': test.description,
                    'duration_minutes': test.duration_minutes
                },
                'message': 'Test créé avec succès'
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
@login_required
def manager_add_question(request, test_id):
    """Ajouter une question à un test"""
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Accès non autorisé'
        }, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Vérifier que le test existe
            test = Test.objects.get(id=test_id)
            
            # Créer la question
            question = Question.objects.create(
                text=data['text'],
                question_type=data.get('question_type', 'multiple_choice'),
                points=data.get('points', 1),
                order=data.get('order', 0),
                test=test
            )
            
            # Ajouter les options si question à choix multiple
            if data.get('options'):
                for option_data in data['options']:
                    from .models import QuestionOption
                    QuestionOption.objects.create(
                        question=question,
                        text=option_data['text'],
                        is_correct=option_data.get('is_correct', False),
                        explanation=option_data.get('explanation', '')
                    )
            
            return JsonResponse({
                'success': True,
                'question': {
                    'id': question.id,
                    'text': question.text,
                    'type': question.question_type,
                    'options_count': question.options.count() if hasattr(question, 'options') else 0
                },
                'message': 'Question ajoutée avec succès'
            })
            
        except Test.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Test non trouvé'
            }, status=404)
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
def manager_get_test_results(request, test_id):
    """Récupérer les résultats d'un test (Manager)"""
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Accès non autorisé'
        }, status=403)
    
    try:
        test = Test.objects.get(id=test_id)
        sessions = TestSession.objects.filter(test=test, status='completed')
        
        results = []
        for session in sessions:
            results.append({
                'session_id': session.id,
                'user_cin': session.user.cin,
                'user_name': session.user.full_name,
                'started_at': session.started_at.isoformat(),
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'score': session.score,
                'passed': session.score >= test.passing_score,
                'duration_seconds': session.duration_seconds
            })
        
        return JsonResponse({
            'success': True,
            'test': {
                'id': test.id,
                'title': test.title,
                'passing_score': test.passing_score
            },
            'results': results,
            'count': len(results),
            'average_score': sum(r['score'] for r in results) / len(results) if results else 0,
            'pass_rate': sum(1 for r in results if r['passed']) / len(results) * 100 if results else 0
        })
        
    except Test.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Test non trouvé'
        }, status=404)


# ==================== API UTILISATEUR (historique) ====================

@login_required
def user_test_history(request):
    """Historique des tests passés par l'utilisateur"""
    user = request.user
    sessions = TestSession.objects.filter(user=user).order_by('-started_at')
    
    history = []
    for session in sessions:
        history.append({
            'session_id': session.id,
            'test_id': session.test.id,
            'test_title': session.test.title,
            'started_at': session.started_at.isoformat(),
            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            'status': session.status,
            'score': session.score,
            'passed': session.score >= session.test.passing_score if session.score else None,
            'duration_seconds': session.duration_seconds
        })
    
    return JsonResponse({
        'success': True,
        'history': history,
        'count': len(history)
    })


@login_required
def user_get_certificate(request, session_id):
    """Générer un certificat pour un test réussi"""
    try:
        session = TestSession.objects.get(id=session_id, user=request.user)
        
        if session.status != 'completed' or session.score < session.test.passing_score:
            return JsonResponse({
                'success': False,
                'error': 'Test non réussi, pas de certificat'
            }, status=400)
        
        # Générer les données du certificat
        certificate_data = {
            'certificate_id': f"CERT-{session.id:06d}",
            'user_name': session.user.full_name,
            'user_cin': session.user.cin,
            'test_title': session.test.title,
            'score': session.score,
            'passing_score': session.test.passing_score,
            'completion_date': session.completed_at.date().isoformat(),
            'valid_until': (session.completed_at.date() + timedelta(days=365)).isoformat(),  # 1 an
            'issuer': 'HSE Training Department'
        }
        
        return JsonResponse({
            'success': True,
            'certificate': certificate_data,
            'download_url': f"/api/certificates/{session.id}/download/"
        })
        
    except TestSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Session non trouvée'
        }, status=404)