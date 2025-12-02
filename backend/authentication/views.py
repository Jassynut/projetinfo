# authentication/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
import qrcode
import io
import base64
from datetime import datetime
from .models import TestUser


# ==================== API POUR MANAGER (PC) ====================

@login_required
def manager_generate_test_qr(request, test_id):
    """
    API pour le MANAGER sur PC: génère un QR code pour un test
    GET: /api/manager/tests/123/generate-qr/
    """
    if request.method == 'GET':
        try:
            # Vérifier si le test existe
            try:
                from tests.models import Test
                test = Test.objects.get(id=test_id)
                test_title = test.title
                test_duration = test.duration_minutes
            except:
                test_title = f"Test #{test_id}"
                test_duration = 30
            
            # Données à encoder dans le QR
            qr_payload = {
                'test_id': test_id,
                'test_title': test_title,
                'action': 'access_test',
                'generated_at': datetime.now().isoformat(),
                'generated_by': request.user.username if request.user.is_authenticated else 'manager',
                'url': f"/test/{test_id}/enter-cin"  # URL React frontend
            }
            
            # Convertir en JSON
            import json as json_module
            qr_string = json_module.dumps(qr_payload)
            
            # Générer QR code
            qr = qrcode.make(qr_string)
            buffer = io.BytesIO()
            qr.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return JsonResponse({
                'success': True,
                'qr_code': f"data:image/png;base64,{qr_base64}",
                'test_info': {
                    'id': test_id,
                    'title': test_title,
                    'duration': test_duration
                },
                'qr_payload': qr_payload,
                'instructions': "Affichez ce QR code aux employés. Ils devront le scanner et entrer leur CIN."
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Méthode non autorisée'
    }, status=405)


# ==================== API POUR UTILISATEUR (MOBILE) ====================

@csrf_exempt
def decode_qr_and_prepare_test(request):
    """
    API appelée quand l'utilisateur scanne le QR code
    POST: {"qr_data": "{\"test_id\": 123, ...}"}
    Retourne les infos du test pour afficher la page de login
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_data_str = data.get('qr_data', '')
            
            if not qr_data_str:
                return JsonResponse({
                    'success': False,
                    'error': 'Données QR manquantes'
                }, status=400)
            
            # Décoder les données QR
            qr_data = json.loads(qr_data_str)
            test_id = qr_data.get('test_id')
            
            if not test_id:
                return JsonResponse({
                    'success': False,
                    'error': 'ID de test manquant dans le QR'
                }, status=400)
            
            # Récupérer les infos du test
            try:
                from tests.models import Test
                test = Test.objects.get(id=test_id)
                
                test_info = {
                    'id': test.id,
                    'title': test.title,
                    'description': test.description,
                    'duration_minutes': test.duration_minutes,
                    'questions_count': test.questions.count() if hasattr(test, 'questions') else 0,
                    'category': test.category.name if test.category else 'Général'
                }
            except Test.DoesNotExist:
                test_info = {
                    'id': test_id,
                    'title': f"Test #{test_id}",
                    'description': 'Test de sécurité',
                    'duration_minutes': 30,
                    'questions_count': 0,
                    'category': 'Général'
                }
            except Exception as e:
                test_info = {
                    'id': test_id,
                    'title': f"Test #{test_id}",
                    'error': f'Infos limitées: {str(e)}'
                }
            
            return JsonResponse({
                'success': True,
                'test': test_info,
                'next_step': 'cin_required',
                'message': 'Veuillez entrer votre CIN pour commencer le test'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Format QR invalide'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur décodage QR: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Méthode non autorisée'
    }, status=405)


@csrf_exempt
def authenticate_and_start_test(request, test_id):
    """
    API pour authentifier l'utilisateur avec son CIN et démarrer le test
    POST: {"cin": "AB123456"}
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cin = data.get('cin', '').strip().upper()
            
            if not cin:
                return JsonResponse({
                    'success': False,
                    'error': 'Veuillez entrer votre CIN'
                }, status=400)
            
            # Vérifier que le test existe
            try:
                from tests.models import Test
                test = Test.objects.get(id=test_id)
            except Test.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Test #{test_id} non trouvé'
                }, status=404)
            
            # 1. Chercher l'employé dans hse_app
            employee_data = None
            try:
                from hse_app.models import Employee
                employee = Employee.objects.get(cin=cin)
                full_name = employee.full_name
                employee_data = {
                    'id': employee.id,
                    'matricule': getattr(employee, 'matricule', ''),
                    'department': getattr(employee, 'department', ''),
                    'position': getattr(employee, 'position', ''),
                    'site': getattr(employee, 'site', ''),
                    'hire_date': employee.hire_date.isoformat() if hasattr(employee, 'hire_date') and employee.hire_date else None
                }
            except Employee.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'CIN non reconnu. Vérifiez votre numéro.'
                }, status=404)
            except Exception as e:
                full_name = None
                print(f"Erreur récupération employé: {e}")
            
            # 2. Chercher ou créer TestUser
            try:
                user = TestUser.objects.get(cin=cin)
                user_exists = True
            except TestUser.DoesNotExist:
                user = TestUser.objects.create_user(
                    cin=cin,
                    full_name=full_name
                )
                user_exists = False
            
            # 3. Authentifier l'utilisateur
            auth_user = authenticate(
                request,
                username=user.username,
                password=cin  # Le CIN est le mot de passe
            )
            
            if auth_user is not None:
                login(request, auth_user)
                
                # 4. Vérifier si l'utilisateur peut passer ce test
                # (Ajouter ici tes règles métier)
                
                # 5. Créer une session de test
                from tests.models import TestSession
                test_session = TestSession.objects.create(
                    test=test,
                    user=user,
                    started_at=datetime.now(),
                    status='in_progress'
                )
                
                # 6. Récupérer les questions
                questions = []
                if hasattr(test, 'questions'):
                    for question in test.questions.all().order_by('?')[:test.questions_count]:
                        questions.append({
                            'id': question.id,
                            'text': question.text,
                            'question_type': question.question_type,
                            'options': [
                                {'id': opt.id, 'text': opt.text, 'is_correct': opt.is_correct}
                                for opt in question.options.all()
                            ] if hasattr(question, 'options') else []
                        })
                
                return JsonResponse({
                    'success': True,
                    'test_session': {
                        'id': test_session.id,
                        'test_id': test.id,
                        'test_title': test.title,
                        'started_at': test_session.started_at.isoformat(),
                        'duration_minutes': test.duration_minutes,
                        'questions_count': len(questions)
                    },
                    'user': {
                        'id': user.id,
                        'cin': user.cin,
                        'full_name': user.full_name,
                        'employee_data': employee_data
                    },
                    'questions': questions,
                    'message': 'Authentification réussie. Test prêt à commencer.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Échec de l\'authentification'
                }, status=401)
                
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
def submit_test_answers(request, test_session_id):
    """
    Soumettre les réponses du test
    POST: {"answers": [{"question_id": 1, "selected_option_id": 3, "answer_text": "..."}, ...]}
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            answers = data.get('answers', [])
            
            # Récupérer la session
            from tests.models import TestSession, TestAnswer
            test_session = TestSession.objects.get(
                id=test_session_id,
                user=request.user
            )
            
            # Enregistrer les réponses
            saved_answers = []
            for answer_data in answers:
                answer = TestAnswer.objects.create(
                    test_session=test_session,
                    question_id=answer_data['question_id'],
                    selected_option_id=answer_data.get('selected_option_id'),
                    answer_text=answer_data.get('answer_text', ''),
                    is_correct=answer_data.get('is_correct', False)
                )
                saved_answers.append({
                    'id': answer.id,
                    'question_id': answer.question_id,
                    'is_correct': answer.is_correct
                })
            
            # Marquer la session comme terminée
            test_session.status = 'completed'
            test_session.completed_at = datetime.now()
            test_session.score = calculate_score(test_session)  # À implémenter
            test_session.save()
            
            return JsonResponse({
                'success': True,
                'test_session': {
                    'id': test_session.id,
                    'status': test_session.status,
                    'score': test_session.score,
                    'completed_at': test_session.completed_at.isoformat()
                },
                'answers_count': len(saved_answers),
                'message': 'Test soumis avec succès'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur soumission: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Méthode non autorisée'
    }, status=405)


# ==================== API UTILITAIRES ====================

@csrf_exempt
@login_required
def get_current_user(request):
    """Récupérer l'utilisateur courant"""
    user = request.user
    return JsonResponse({
        'success': True,
        'user': {
            'id': user.id,
            'cin': user.cin,
            'username': user.username,
            'full_name': user.full_name,
            'is_staff': user.is_staff
        }
    })


@csrf_exempt
def logout_user(request):
    """Déconnexion"""
    logout(request)
    return JsonResponse({'success': True, 'message': 'Déconnecté'})


def calculate_score(test_session):
    """Calculer le score (à adapter selon ta logique métier)"""
    # Exemple simple
    answers = test_session.answers.all()
    correct_count = sum(1 for a in answers if a.is_correct)
    total = answers.count()
    return (correct_count / total * 100) if total > 0 else 0