from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
import qrcode
import io
import base64
from datetime import datetime
from authentication.models import TestUser

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authentication.importExcel import importexcel

# ==================== API POUR MANAGER (PC) ====================
# Authentification: full_name (username) + CIN (mot de passe)

@csrf_exempt
def manager_login(request):
    """
    API pour authentifier un manager HSE.
    POST: {"full_name": "Fatima Zohra", "cin": "AB123456"}
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            full_name = data.get('full_name', '').strip()
            cin = data.get('cin', '').strip().upper()

            if not full_name or not cin:
                return JsonResponse({
                    'success': False,
                    'error': 'Nom complet et CIN requis'
                }, status=400)

            user = authenticate(request, full_name=full_name, cin=cin)

            if user is not None and user.is_manager:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'full_name': user.full_name,
                        'username': user.username,
                        'user_type': user.user_type,
                        'is_staff': user.is_staff
                    },
                    'message': 'Connexion manager réussie'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Identifiants incorrects ou utilisateur non autorisé'
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


@login_required
def manager_generate_test_qr(request, test_id):
    """
    API pour le MANAGER sur PC: génère un QR code pour un test
    GET: /api/manager/tests/123/generate-qr/
    """
    if not request.user.is_manager:
        return JsonResponse({
            'success': False,
            'error': 'Accès réservé aux managers'
        }, status=403)

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
                'generated_by': request.user.full_name,
                'url': f"http://10.26.31.10:5173/qr-login/{test_id}"
} 

            # Convertir en JSON
            qr_string = json.dumps(qr_payload)

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


# ==================== API POUR UTILISATEUR HSE (MOBILE) ====================
# Authentification: CIN uniquement (1 seul champ après scan QR)

@csrf_exempt
def decode_qr_and_prepare_test(request):
    """
    API appelée quand l'utilisateur scanne le QR code
    POST: {"qr_data": "{\"test_id\": 123, ...}"}
    Retourne les infos du test pour afficher la page de saisie CIN
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
            except Exception:
                test_info = {
                    'id': test_id,
                    'title': f"Test #{test_id}",
                    'description': 'Test de sécurité',
                    'duration_minutes': 30,
                    'questions_count': 0,
                    'category': 'Général'
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
def authenticate_hse_user_and_start_test(request, test_id):
    """
    API pour authentifier un utilisateur HSE avec son CIN et démarrer le test.
    UN SEUL CHAMP: CIN
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

            user = authenticate(request, cin=cin)

            if user is None:
                return JsonResponse({
                    'success': False,
                    'error': 'CIN non reconnu. Vérifiez votre numéro.'
                }, status=401)

            # Vérifier que c'est bien un utilisateur HSE (pas un manager)
            if user.is_manager:
                return JsonResponse({
                    'success': False,
                    'error': 'Utilisez l\'interface manager pour vous connecter.'
                }, status=403)

            # Connecter l'utilisateur
            login(request, user)

            # Récupérer les données employé depuis hse_app
            employee_data = None
            try:
                from hse_app.models import HSEUser
                hse_user = HSEUser.objects.get(cin=cin)
                employee_data = {
                    'id': hse_user.id,
                    'full_name': hse_user.full_name,
                    'matricule': getattr(hse_user, 'matricule', ''),
                    'department': getattr(hse_user, 'department', ''),
                    'position': getattr(hse_user, 'position', ''),
                    'site': getattr(hse_user, 'site', ''),
                }
            except Exception:
                pass

            # Créer une session de test
            try:
                from tests.models import TestAttempt
                test_session = TestAttempt.objects.create(
                    test=test,
                    user=user,
                    started_at=datetime.now(),
                    status='in_progress'
                )
                session_id = test_session.id
            except Exception:
                session_id = None

            # Récupérer les questions
            questions = []
            if hasattr(test, 'questions'):
                for question in test.questions.all().order_by('?'):
                    questions.append({
                        'id': question.id,
                        'text': question.text,
                        'question_type': getattr(question, 'question_type', 'multiple_choice'),
                        'options': [
                            {'id': opt.id, 'text': opt.text}
                            for opt in question.options.all()
                        ] if hasattr(question, 'options') else []
                    })

            return JsonResponse({
                'success': True,
                'test_session': {
                    'id': session_id,
                    'test_id': test.id,
                    'test_title': test.title,
                    'started_at': datetime.now().isoformat(),
                    'duration_minutes': test.duration_minutes,
                    'questions_count': len(questions)
                },
                'user': {
                    'id': user.id,
                    'cin': user.cin,
                    'full_name': user.full_name,
                    'user_type': user.user_type,
                    'employee_data': employee_data
                },
                'questions': questions,
                'message': 'Authentification réussie. Test prêt à commencer.'
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
def submit_test_answers(request, test_session_id):
    """
    Soumettre les réponses du test
    POST: {"answers": [{"question_id": 1, "selected_option_id": 3}, ...]}
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            answers = data.get('answers', [])

            from tests.models import TestAttempt, TestAnswer
            test_session = TestAttempt.objects.get(
                id=test_session_id,
                user=request.user
            )

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

            test_session.status = 'completed'
            test_session.completed_at = datetime.now()
            test_session.score = calculate_score(test_session)
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
            'user_type': user.user_type,
            'is_manager': user.is_manager,
            'is_staff': user.is_staff
        }
    })


@csrf_exempt
def logout_user(request):
    """Déconnexion"""
    logout(request)
    return JsonResponse({'success': True, 'message': 'Déconnecté'})


def calculate_score(test_session):
    """Calculer le score"""
    answers = test_session.answers.all()
    correct_count = sum(1 for a in answers if a.is_correct)
    total = answers.count()
    return (correct_count / total * 100) if total > 0 else 0

#==================== API POUR IMPORTER APPRENANTS ====================

class UploadApprenantsView(APIView):
    """
    Upload d'un fichier Excel pour importer des apprenants HSE.
    """
    def post(self, request):
        excel_file = request.FILES.get("file")

        if not excel_file:
            return Response(
                {"error": "Aucun fichier n'a été envoyé."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Appel du service d'import
        result = importexcel(excel_file)

        if result.get("status") == "error":
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_201_CREATED)

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

    return JsonResponse({"success": False, "error": "Méthode non autorisée"})