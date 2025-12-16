from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.cache import cache
from django.db import IntegrityError

from .models import Test, TestAttempt, Question
from .serializers_api import (
    TestListSerializer, TestDetailSerializer, TestCreateUpdateSerializer,
    TestAttemptListSerializer, TestAttemptDetailSerializer,
    TestAttemptStartSerializer, TestAttemptSubmitSerializer,
    QuestionDetailSerializer
)
from hse_app.models import HSEUser

# =============================================================================
# VIEWSETS TESTS
# =============================================================================

class TestViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les tests HSE
    
    Endpoints:
    - GET /api/tests/ - Lister tous les tests actifs
    - POST /api/tests/ - Créer un test (Admin seulement)
    - GET /api/tests/{id}/ - Détails d'un test
    - PUT /api/tests/{id}/ - Modifier un test (Admin seulement)
    - PATCH /api/tests/{id}/ - Modification partielle (Admin seulement)
    - DELETE /api/tests/{id}/ - Supprimer un test (Admin seulement)
    - GET /api/tests/{id}/results/ - Résultats du test
    """
    
    queryset = Test.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TestCreateUpdateSerializer
        return TestListSerializer
    
    def get_queryset(self):
        queryset = Test.objects.all()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        # Filtrer par version
        version = self.request.query_params.get('version')
        if version:
            queryset = queryset.filter(version=version)
        
        return queryset.order_by('version')
    
    def create(self, request, *args, **kwargs):
        """Créer un nouveau test (Admin seulement)"""
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': 'Accès refusé. Seuls les administrateurs peuvent créer des tests.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Récupérer les résultats d'un test"""
        test = self.get_object()
        attempts = TestAttempt.objects.filter(test=test, status='passed').order_by('-completed_at')
        
        serializer = TestAttemptListSerializer(attempts, many=True)
        
        total_attempts = TestAttempt.objects.filter(test=test).count()
        passed_attempts = attempts.count()
        
        return Response({
            'success': True,
            'test_version': test.version,
            'total_attempts': total_attempts,
            'passed_attempts': passed_attempts,
            'pass_rate': round((passed_attempts / total_attempts * 100) if total_attempts > 0 else 0, 1),
            'results': serializer.data
        })


# =============================================================================
# VIEWSETS TEST ATTEMPTS
# =============================================================================

class TestAttemptViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les tentatives de test
    
    Endpoints:
    - GET /api/test-attempts/ - Lister mes tentatives
    - POST /api/test-attempts/start/ - Démarrer un test
    - GET /api/test-attempts/{id}/ - Détails d'une tentative
    - POST /api/test-attempts/{id}/submit/ - Soumettre les réponses
    """
    
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestAttemptDetailSerializer
        elif self.action == 'start':
            return TestAttemptStartSerializer
        elif self.action == 'submit':
            return TestAttemptSubmitSerializer
        return TestAttemptListSerializer
    
    def get_queryset(self):
        """Retourner uniquement les tentatives de l'utilisateur actuel"""
        return TestAttempt.objects.filter(user=self.request.user).order_by('-started_at')
    
    @action(detail=False, methods=['post'])
    def start(self, request):
        """Démarrer une nouvelle tentative de test"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        test_id = serializer.validated_data['test_id']
        langue = serializer.validated_data['langue']
        
        try:
            test = Test.objects.get(id=test_id, is_active=True)
        except Test.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Test non trouvé'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier si une tentative est déjà en cours
        existing_attempt = TestAttempt.objects.filter(
            user=request.user,
            test=test,
            status='in_progress'
        ).first()
        
        if existing_attempt:
            return Response({
                'success': True,
                'message': 'Tentative déjà en cours',
                'attempt': TestAttemptDetailSerializer(existing_attempt).data
            })
        
        # Créer une nouvelle tentative
        attempt = TestAttempt.objects.create(
            user=request.user,
            test=test,
            langue=langue,
            status='in_progress',
            mandatory_total=test.mandatory_questions_count,
            optional_total=test.optional_questions_count
        )
        
        serializer = TestAttemptDetailSerializer(attempt)
        return Response({
            'success': True,
            'message': 'Test démarré',
            'attempt': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Soumettre les réponses et calculer le score"""
        attempt = self.get_object()
        
        # Vérifier que l'utilisateur peut soumettre cette tentative
        if attempt.user != request.user:
            return Response({
                'success': False,
                'error': 'Accès refusé'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Vérifier que la tentative est en cours
        if attempt.status != 'in_progress':
            return Response({
                'success': False,
                'error': 'Cette tentative n\'est pas en cours'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_answers = serializer.validated_data['user_answers']
        time_taken = serializer.validated_data.get('time_taken_seconds', 0)
        
        # Stocker les réponses
        attempt.user_answers = user_answers
        attempt.time_taken_seconds = time_taken
        attempt.completed_at = timezone.now()
        
        # Calculer les scores
        scores = attempt.calculate_scores()
        
        attempt.mandatory_correct = scores['mandatory']
        attempt.optional_correct = scores['optional']
        attempt.passed = scores['passed']
        attempt.status = 'passed' if scores['passed'] else 'failed'
        
        # Calculer les pourcentages
        attempt.mandatory_score_percentage = (scores['mandatory'] / attempt.mandatory_total * 100) if attempt.mandatory_total > 0 else 0
        attempt.optional_score_percentage = (scores['optional'] / attempt.optional_total * 100) if attempt.optional_total > 0 else 0
        attempt.overall_score_percentage = ((scores['mandatory'] + scores['optional']) / (attempt.mandatory_total + attempt.optional_total) * 100) if (attempt.mandatory_total + attempt.optional_total) > 0 else 0
        
        attempt.save()
        
        # Mettre à jour le score et sensibilise_avec_succes de l'utilisateur HSE si lié
        if attempt.passed:
            try:
                # Trouver l'utilisateur HSE correspondant via le CIN
                hse_user = HSEUser.objects.get(cin=attempt.user.cin)
                # Mettre à jour sensibilise_avec_succes si le test est réussi
                hse_user.sensibilise_avec_succes = True
                # Score = (pourcentage / 100) * 21 (si le champ existe)
                if hasattr(hse_user, 'score'):
                    hse_user.score = round((attempt.overall_score_percentage / 100) * 21)
                # Note: Le champ 'presence' n'est pas mis à jour automatiquement
                # Il doit être géré manuellement par un manager
                hse_user.save(update_fields=['sensibilise_avec_succes'] + (['score'] if hasattr(hse_user, 'score') else []))
            except HSEUser.DoesNotExist:
                pass
            except Exception as e:
                # Logger l'erreur mais ne pas bloquer la soumission du test
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Erreur lors de la mise à jour de sensibilise_avec_succes: {str(e)}")
        
        response_data = TestAttemptDetailSerializer(attempt).data
        response_data['scores'] = scores
        
        return Response({
            'success': True,
            'message': 'Test soumis avec succès',
            'attempt': response_data
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_test_attempts(request):
    """Récupérer toutes les tentatives de l'utilisateur"""
    attempts = TestAttempt.objects.filter(user=request.user).order_by('-started_at')
    
    serializer = TestAttemptListSerializer(attempts, many=True)
    
    return Response({
        'success': True,
        'user_cin': request.user.cin,
        'attempts_count': attempts.count(),
        'passed_count': attempts.filter(passed=True).count(),
        'attempts': serializer.data
    })


# =============================================================================
# ALIAS / ENDPOINTS FRONTEND COMPAT (versions/questions publics)
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def list_versions(request):
    if request.method == 'POST':
        # Création simplifiée : si version non fournie, auto-increment
        version = request.data.get('version')
        description = request.data.get('description') or request.data.get('name') or ''
        if not version:
            last = Test.objects.order_by('-version').first()
            version = (last.version + 1) if last else 1
        try:
            version = int(version)
        except (TypeError, ValueError):
            return Response({'success': False, 'error': 'Version invalide. Doit être un nombre entier positif.'}, status=400)
        
        # Validation : Version doit être un entier positif
        if version < 1:
            return Response({
                'success': False, 
                'error': f'Version invalide. La version doit être un nombre entier positif (>= 1). Vous avez fourni : {version}'
            }, status=400)
        try:
            # Récupérer toutes les questions actives de la base de données
            all_active_questions = Question.objects.filter(is_active=True).order_by('question_code')
            question_ids = [q.id for q in all_active_questions]
            
            # Déterminer les questions obligatoires (celles avec is_mandatory=True)
            mandatory_question_ids = [q.id for q in all_active_questions if q.is_mandatory]
            
            # Si aucune question n'est marquée comme obligatoire, prendre les 9 premières par défaut
            if not mandatory_question_ids and len(question_ids) >= 9:
                mandatory_question_ids = question_ids[:9]
            elif not mandatory_question_ids:
                mandatory_question_ids = question_ids  # Prendre toutes les questions si moins de 9
            
            test = Test.objects.create(
                version=version,
                description=description,
                ordre_questions=question_ids,  # Toutes les questions actives par défaut
                mandatory_questions=mandatory_question_ids,  # Questions obligatoires
                total_questions=len(question_ids),  # Nombre total de questions
                mandatory_questions_count=len(mandatory_question_ids),
                is_active=True,
            )
        except IntegrityError as exc:
            return Response({'success': False, 'error': str(exc)}, status=400)
        except Exception as exc:
            return Response({'success': False, 'error': str(exc)}, status=500)
        # Forcer le recalcul de questions_count
        test.refresh_from_db()
        
        return Response(
            {
                'success': True,
                'message': f'Version {test.version} créée avec {len(question_ids)} question(s) ajoutée(s) automatiquement',
                'version': {
                    'id': test.id,
                    'version': test.version,
                    'description': test.description,
                    'name': f"Version {test.version}",
                    'total_questions': test.total_questions,
                    'questions_count': test.questions_count,  # Inclure questions_count
                    'ordre_questions': test.ordre_questions,  # Inclure ordre_questions pour référence
                    'created_at': test.created_at,
                },
            },
            status=201,
        )

    import logging
    logger = logging.getLogger(__name__)
    
    try:
        qs = Test.objects.all().order_by('version')
        count = qs.count()
        logger.info(f"Nombre de versions trouvées dans la base de données: {count}")
        
        data = []
        for t in qs:
            try:
                item = TestListSerializer(t).data
                item['name'] = f"Version {t.version}"
                # Calculer questions_count depuis ordre_questions (source de vérité)
                if t.ordre_questions:
                    questions_count = len(t.ordre_questions)
                else:
                    questions_count = 0
                item['questions_count'] = questions_count
                item['total_questions'] = questions_count  # Synchroniser total_questions avec questions_count
                # S'assurer que created_at est inclus
                if hasattr(t, 'created_at') and t.created_at:
                    item['created_at'] = t.created_at.isoformat() if hasattr(t.created_at, 'isoformat') else str(t.created_at)
                data.append(item)
            except Exception as e:
                logger.error(f"Erreur lors de la sérialisation de la version {t.id}: {str(e)}")
                continue
        
        logger.info(f"Retour de {len(data)} versions depuis list_versions")
        return Response({'versions': data})
    except Exception as e:
        logger.error(f"Erreur dans list_versions: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': f'Erreur lors de la récupération des versions: {str(e)}',
            'versions': []
        }, status=500)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def list_active_versions(request):
    qs = Test.objects.filter(is_active=True).order_by('version')
    serializer = TestListSerializer(qs, many=True)
    data = serializer.data
    # ajouter 'name' et s'assurer que questions_count est correct
    test_list = list(qs)  # Convertir en liste pour éviter les requêtes multiples
    for idx, item in enumerate(data):
        item['name'] = f"Version {item.get('version')}"
        # Calculer questions_count depuis ordre_questions (source de vérité)
        if idx < len(test_list):
            test_obj = test_list[idx]
            if test_obj.ordre_questions:
                questions_count = len(test_obj.ordre_questions)
            else:
                questions_count = 0
            item['questions_count'] = questions_count
            item['total_questions'] = questions_count  # Synchroniser total_questions
    return Response({'versions': data})


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.AllowAny])
def version_detail(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.method == 'GET':
        data = TestDetailSerializer(test).data
        data['name'] = f"Version {test.version}"
        # S'assurer que ordre_questions est inclus (déjà dans le serializer maintenant)
        # Retourner dans un format cohérent avec le frontend
        return Response({'version': data})
    if request.method == 'PUT':
        description = request.data.get('description') or ''
        version = request.data.get('version') or request.data.get('name')
        try:
            if version:
                test.version = int(version) if str(version).isdigit() else test.version
        except (TypeError, ValueError):
            pass
        test.description = description
        test.save()
        data = TestDetailSerializer(test).data
        data['name'] = f"Version {test.version}"
        return Response({'success': True, 'version': data})
    # DELETE
    import logging
    from django.db import connection
    logger = logging.getLogger(__name__)
    
    try:
        # Supprimer directement via SQL pour éviter les problèmes de cascade avec les certificats
        with connection.cursor() as cursor:
            # Supprimer d'abord les tentatives associées
            cursor.execute("DELETE FROM tests_testattempt WHERE test_id = %s", [test.id])
            # Supprimer le test
            cursor.execute("DELETE FROM tests_test WHERE id = %s", [test.id])
        
        return Response({'success': True, 'message': 'Version supprimée avec succès'})
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la version {pk}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Si erreur SQL, essayer avec l'ORM mais en gérant les erreurs de certificats
        try:
            from tests.models import TestAttempt
            # Supprimer les tentatives
            TestAttempt.objects.filter(test=test).delete()
            # Supprimer le test
            test.delete()
            return Response({'success': True, 'message': 'Version supprimée avec succès'})
        except Exception as e2:
            error_str = str(e2).lower()
            # Si l'erreur est liée aux certificats, ignorer et supprimer quand même
            if 'certificat' in error_str or 'certificate' in error_str:
                logger.warning(f"Erreur liée aux certificats ignorée: {error_str}")
                # Forcer la suppression via SQL brut
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM tests_test WHERE id = %s", [test.id])
                    return Response({'success': True, 'message': 'Version supprimée avec succès'})
                except Exception as e3:
                    return Response({
                        'success': False, 
                        'error': f'Erreur lors de la suppression: {str(e3)}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    'success': False, 
                    'error': f'Erreur lors de la suppression: {str(e2)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def version_questions(request, pk):
    test = get_object_or_404(Test, pk=pk)
    questions = test.get_questions_in_order()
    serializer = QuestionDetailSerializer(questions, many=True)
    return Response({'questions': serializer.data, 'version': test.version})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def version_add_question(request, pk):
    test = get_object_or_404(Test, pk=pk)
    question_id = request.data.get('question_id')
    if not question_id:
        return Response({'success': False, 'error': 'question_id requis'}, status=400)
    try:
        qid = int(question_id)
        Question.objects.get(id=qid)
    except (ValueError, Question.DoesNotExist):
        return Response({'success': False, 'error': 'Question introuvable'}, status=404)

    ordre = list(test.ordre_questions or [])
    if qid not in ordre:
        ordre.append(qid)
        test.ordre_questions = ordre
        test.total_questions = len(ordre)
        test.save()
    return Response({'success': True, 'ordre_questions': test.ordre_questions})


@api_view(['PATCH'])
@permission_classes([permissions.AllowAny])
def version_update_order(request, pk):
    """Mettre à jour l'ordre des questions d'une version"""
    test = get_object_or_404(Test, pk=pk)
    ordre_questions = request.data.get('ordre_questions')
    
    if ordre_questions is None:
        return Response({'success': False, 'error': 'ordre_questions requis'}, status=400)
    
    if not isinstance(ordre_questions, list):
        return Response({'success': False, 'error': 'ordre_questions doit être une liste'}, status=400)
    
    # Vérifier que tous les IDs sont valides
    for qid in ordre_questions:
        try:
            Question.objects.get(id=qid)
        except Question.DoesNotExist:
            return Response({'success': False, 'error': f'Question avec ID {qid} non trouvée'}, status=404)
    
    test.ordre_questions = ordre_questions
    test.total_questions = len(ordre_questions)  # Mettre à jour total_questions selon ordre_questions
    test.save()
    
    # Forcer le recalcul de questions_count en rechargant l'objet
    test.refresh_from_db()
    
    return Response({
        'success': True,
        'ordre_questions': test.ordre_questions,
        'total_questions': test.total_questions,
        'questions_count': test.questions_count  # Inclure questions_count dans la réponse
    })


# =============================================================================
# ENDPOINTS APPRENANT (compat maquette sans authentification)
# =============================================================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_cni(request):
    cin = request.data.get('cni', '').strip().upper()
    if not cin:
        return Response({'success': False, 'error': 'CNI requis'}, status=400)
    exists = HSEUser.objects.filter(cin=cin).exists()
    return Response({'success': exists})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def test_questions_public(request, test_id):
    test = get_object_or_404(Test, id=test_id, is_active=True)
    questions = test.get_questions_in_order()
    serializer = QuestionDetailSerializer(questions, many=True, context={'request': request})
    return Response({'questions': serializer.data, 'test_id': test.id, 'version': test.version})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def test_submit_answer(request, test_id):
    # Stockage léger en cache par session key
    question_id = request.data.get('question_id')
    answer = request.data.get('answer')
    if question_id is None:
        return Response({'success': False, 'error': 'question_id requis'}, status=400)
    cache_key = f"test_answers:{request.session.session_key}:{test_id}"
    answers = cache.get(cache_key, {})
    answers[str(question_id)] = {'answer': answer}
    cache.set(cache_key, answers, 60 * 30)
    return Response({'success': True})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def test_finish_public(request, test_id):
    from django.utils import timezone
    from authentication.models import TestUser
    from hse_app.models import HSEUser
    
    test = get_object_or_404(Test, id=test_id)
    provided_answers = request.data.get('answers') or {}
    cin = request.data.get('cin', '').strip().upper()
    langue = request.data.get('langue', 'fr')
    time_taken = request.data.get('time_taken_seconds', 0)
    # Utiliser l'état fourni, sinon celui du test, sinon test_final par défaut
    etat = request.data.get('etat', getattr(test, 'etat', 'test_final'))
    
    cache_key = f"test_answers:{request.session.session_key}:{test_id}"
    cached_answers = cache.get(cache_key, {})
    # merge (answers payload has priority)
    cached_answers.update(provided_answers)

    mandatory_correct = 0
    optional_correct = 0
    mandatory_ids = set(test.mandatory_questions or [])
    user_answers_dict = {}

    for qid_str, data in cached_answers.items():
        try:
            qid = int(qid_str)
            question = Question.objects.get(id=qid)
        except (ValueError, Question.DoesNotExist):
            continue
        
        # Extraire la réponse de l'utilisateur
        # Le format peut être soit {"answer": bool} (du cache) soit directement bool (du frontend)
        if isinstance(data, dict):
            user_answer = data.get('answer')
        else:
            user_answer = data
        
        # Normaliser la réponse en booléen si nécessaire
        # Gérer les cas où la réponse arrive comme chaîne "true"/"false" ou entier 1/0
        if isinstance(user_answer, str):
            user_answer = user_answer.lower().strip()
            if user_answer in ['true', 'vrai', '1', 'yes', 'oui', 't']:
                user_answer = True
            elif user_answer in ['false', 'faux', '0', 'no', 'non', 'f']:
                user_answer = False
            else:
                continue  # Réponse invalide, passer à la suivante
        elif isinstance(user_answer, int):
            user_answer = bool(user_answer)
        elif user_answer is None:
            continue  # Pas de réponse, passer à la suivante
        
        # Vérifier la réponse en utilisant la méthode check_answer du modèle
        is_correct = question.check_answer(user_answer)
        
        # Encoder la réponse dans la langue choisie
        answer_text = None
        if langue == 'fr':
            answer_text = 'Oui' if user_answer else 'Non'
        elif langue == 'en':
            answer_text = 'Yes' if user_answer else 'No'
        elif langue == 'ar':
            answer_text = 'نعم' if user_answer else 'لا'
        else:
            answer_text = 'Oui' if user_answer else 'Non'  # Par défaut français
        
        # Stocker la réponse avec le booléen ET le texte dans la langue choisie
        user_answers_dict[str(qid)] = {
            'answer': user_answer,  # Booléen pour le calcul
            'answer_text': answer_text,  # Texte dans la langue choisie
            'langue': langue  # Langue utilisée
        }
        
        # Déterminer si la question est obligatoire
        is_mandatory_question = qid in mandatory_ids or question.is_mandatory
        
        if is_mandatory_question:
            if is_correct:
                mandatory_correct += 1
        else:
            if is_correct:
                optional_correct += 1

    total_score = mandatory_correct + optional_correct
    # Calculer le total des questions obligatoires RÉPONDUES par l'utilisateur
    # On ne compte que les questions obligatoires présentes dans cached_answers
    total_mandatory = 0
    for qid_str in cached_answers.keys():
        try:
            qid = int(qid_str)
            question = Question.objects.get(id=qid)
            is_mandatory_question = qid in mandatory_ids or question.is_mandatory
            if is_mandatory_question:
                total_mandatory += 1
        except (ValueError, Question.DoesNotExist):
            continue
    total_optional = len(cached_answers) - total_mandatory
    
    # Calculer les pourcentages
    mandatory_score_percentage = (mandatory_correct / total_mandatory * 100) if total_mandatory > 0 else 0
    optional_score_percentage = (optional_correct / total_optional * 100) if total_optional > 0 else 0
    overall_score_percentage = (total_score / test.total_questions * 100) if test.total_questions > 0 else 0
    
    # Déterminer si le test est réussi (toutes les questions obligatoires doivent être correctes)
    passed = (mandatory_correct == total_mandatory) if total_mandatory > 0 else False
    
    # Créer ou récupérer TestUser si CIN fourni
    test_user = None
    attempt = None
    error_message = None
    
    if cin:
        try:
            # Vérifier que le CIN existe dans HSEUser
            try:
                hse_user = HSEUser.objects.get(cin=cin)
            except HSEUser.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'CIN {cin} non trouvé dans la base de données. Veuillez contacter l\'administrateur.'
                }, status=404)
            
            # Créer ou récupérer TestUser
            test_user, created = TestUser.objects.get_or_create(
                cin=cin,
                defaults={
                    'username': f"user_{cin}",
                    'full_name': hse_user.full_name or f"User {cin}",
                    'user_type': 'user'
                }
            )
            
            # Créer ou mettre à jour TestAttempt (get_or_create pour éviter les doublons)
            attempt, created = TestAttempt.objects.get_or_create(
                test=test,
                user=test_user,
                defaults={
                    'langue': langue,
                    'etat': etat,
                    'user_answers': user_answers_dict,
                    'mandatory_correct': mandatory_correct,
                    'optional_correct': optional_correct,
                    'mandatory_total': total_mandatory,
                    'optional_total': total_optional,
                    'mandatory_score_percentage': round(mandatory_score_percentage, 2),
                    'optional_score_percentage': round(optional_score_percentage, 2),
                    'overall_score_percentage': round(overall_score_percentage, 2),
                    'passed': passed,
                    'status': 'passed' if passed else 'failed',
                    'time_taken_seconds': time_taken,
                    'completed_at': timezone.now()
                }
            )
            
            # Si l'attempt existe déjà, mettre à jour ses données
            if not created:
                attempt.langue = langue
                attempt.etat = etat
                attempt.user_answers = user_answers_dict
                attempt.mandatory_correct = mandatory_correct
                attempt.optional_correct = optional_correct
                attempt.mandatory_total = total_mandatory
                attempt.optional_total = total_optional
                attempt.mandatory_score_percentage = round(mandatory_score_percentage, 2)
                attempt.optional_score_percentage = round(optional_score_percentage, 2)
                attempt.overall_score_percentage = round(overall_score_percentage, 2)
                attempt.passed = passed
                attempt.status = 'passed' if passed else 'failed'
                attempt.time_taken_seconds = time_taken
                attempt.completed_at = timezone.now()
                attempt.save()
            
            # Mettre à jour sensibilise_avec_succes dans HSEUser
            try:
                hse_user.sensibilise_avec_succes = passed
                hse_user.save(update_fields=['sensibilise_avec_succes'])
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Erreur mise à jour sensibilise_avec_succes: {str(e)}")
            
            # Générer automatiquement un certificat uniquement si le test est réussi ET si c'est un test final
            if passed and attempt and attempt.etat == 'test_final':
                try:
                    from certificats.models import Certificate
                    from datetime import datetime, timedelta
                    import uuid
                    from django.db import connection
                    
                    # Vérifier si la table certificats_certificate existe
                    table_exists = False
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("SHOW TABLES LIKE 'certificats_certificate'")
                            table_exists = cursor.fetchone() is not None
                    except Exception:
                        table_exists = False
                    
                    if table_exists:
                        # Vérifier si un certificat existe déjà pour cette tentative
                        try:
                            existing_certificate = Certificate.objects.filter(test_attempt=attempt).first()
                            if not existing_certificate:
                                # Créer un nouveau certificat
                                user_full_name = hse_user.get_full_name() or hse_user.nom or f"User {cin}"
                                user_cin = cin
                                
                                certificate_number = f"HSE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
                                expiry_date = (datetime.now() + timedelta(days=365)).date()
                                
                                certificate = Certificate.objects.create(
                                    test_attempt=attempt,
                                    certificate_number=certificate_number,
                                    user_full_name=user_full_name,
                                    user_cin=user_cin,
                                    test_version=test.version,
                                    score=int(overall_score_percentage),
                                    expiry_date=expiry_date
                                )
                                import logging
                                logger = logging.getLogger(__name__)
                                logger.info(f"Certificat créé avec succès: {certificate.id} pour attempt {attempt.id}")
                        except Exception as cert_error:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Erreur création certificat: {str(cert_error)}")
                            import traceback
                            logger.error(traceback.format_exc())
                    else:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning("Table certificats_certificate n'existe pas. Certificat non généré.")
                except ImportError:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning("Module certificats non disponible. Certificat non généré.")
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Erreur génération certificat: {str(e)}")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur création TestAttempt: {str(e)}")
            error_message = f"Erreur lors de l'enregistrement: {str(e)}"
    else:
        error_message = "CIN non fourni. Impossible d'enregistrer le test."
    
    # Récupérer l'ID du certificat si généré (pour le cache aussi)
    certificate_id_for_cache = None
    if attempt:
        try:
            from certificats.models import Certificate
            from django.db import connection
            
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SHOW TABLES LIKE 'certificats_certificate'")
                    table_exists = cursor.fetchone() is not None
            except Exception:
                table_exists = False
            
            if table_exists:
                try:
                    cert = Certificate.objects.filter(test_attempt=attempt).first()
                    if cert:
                        certificate_id_for_cache = str(cert.id)
                except Exception:
                    pass
        except Exception:
            pass
    
    # Stocker aussi dans le cache pour compatibilité
    cache.set(f"test_result:{request.session.session_key}:{test_id}", {
        'score': total_score,
        'mandatory_correct': mandatory_correct,
        'optional_correct': optional_correct,
        'test_version': test.version,
        'attempt_id': attempt.id if attempt else None,
        'passed': passed,
        'certificate_id': certificate_id_for_cache,
        'total_questions': test.total_questions,
        'mandatory_total': total_mandatory,
        'optional_total': total_optional
    }, 60 * 30)
    cache.delete(cache_key)

    # Retourner la réponse
    if error_message:
        return Response({
            'success': False,
            'error': error_message
        }, status=400)
    
    if not attempt:
        return Response({
            'success': False,
            'error': 'Impossible de créer l\'enregistrement du test. CIN non trouvé.'
        }, status=400)
    
    # Récupérer l'ID du certificat si généré
    certificate_id = None
    if attempt:
        try:
            from certificats.models import Certificate
            from django.db import connection
            
            # Vérifier si la table existe avant d'essayer d'accéder à la relation
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SHOW TABLES LIKE 'certificats_certificate'")
                    table_exists = cursor.fetchone() is not None
            except Exception:
                table_exists = False
            
            if table_exists:
                try:
                    certificate = Certificate.objects.filter(test_attempt=attempt).first()
                    if certificate:
                        certificate_id = str(certificate.id)
                except Exception:
                    pass
        except ImportError:
            pass
        except Exception:
            pass
    
    return Response({
        'success': True,
        'score': total_score,
        'mandatory_correct': mandatory_correct,
        'optional_correct': optional_correct,
        'total_questions': test.total_questions,
        'mandatory_total': total_mandatory,
        'optional_total': total_optional,
        'overall_score_percentage': round(overall_score_percentage, 2),
        'mandatory_score_percentage': round(mandatory_score_percentage, 2),
        'optional_score_percentage': round(optional_score_percentage, 2),
        'passed': passed,
        'attempt_id': attempt.id if attempt else None,
        'certificate_id': certificate_id,
        'cin': cin if cin else None,
        'message': 'Test enregistré avec succès'
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def test_result_public(request, test_id):
    data = cache.get(f"test_result:{request.session.session_key}:{test_id}")
    if not data:
        return Response({'success': False, 'error': 'Résultat indisponible'}, status=404)
    return Response({
        'success': True,
        'score': data.get('score'),
        'test_version': data.get('test_version'),
        'attempt_id': data.get('attempt_id'),
        'certificate_id': data.get('certificate_id'),
        'passed': data.get('passed'),
        'mandatory_correct': data.get('mandatory_correct'),
        'mandatory_total': data.get('mandatory_total'),
        'optional_correct': data.get('optional_correct'),
        'optional_total': data.get('optional_total'),
        'total_questions': data.get('total_questions'),
        'overall_score_percentage': data.get('overall_score_percentage'),
    })


from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Question, Test
from .serializers_api import QuestionDetailSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    """
    CRUD basique des questions pour compatibilité frontend
    """
    queryset = Question.objects.all().order_by('question_code')
    serializer_class = QuestionDetailSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None  # Désactiver la pagination pour retourner toutes les questions

    @action(detail=True, methods=['post'], url_path='associate_version')
    def associate_version(self, request, pk=None):
        """
        Associer cette question à une version de test
        
        POST /api/questions/{id}/associate_version/
        Body: { "test_id": 1 } ou { "version_id": 1 }
        """
        question = self.get_object()
        
        # Accepte test_id ou version_id
        test_id = request.data.get('test_id') or request.data.get('version_id')
        
        if not test_id:
            return Response({
                'success': False,
                'error': 'test_id ou version_id est requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Chercher le test par ID
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            # Peut-être essayer par numéro de version
            try:
                test = Test.objects.get(version=test_id)
            except (Test.DoesNotExist, ValueError):
                return Response({
                    'success': False,
                    'error': f'Test avec ID/version {test_id} non trouvé'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier si la question est déjà dans le test
        ordre = list(test.ordre_questions or [])
        
        if question.id in ordre:
            return Response({
                'success': False,
                'error': f'La question est déjà dans le test version {test.version}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Ajouter la question
        ordre.append(question.id)
        test.ordre_questions = ordre
        test.total_questions = len(ordre)
        test.save()
        
        return Response({
            'success': True,
            'message': f'Question "{question.question_code}" ajoutée au test version {test.version}',
            'test_id': test.id,
            'version': test.version,
            'question_id': question.id,
            'total_questions_in_test': test.total_questions
        })
    
    def create(self, request, *args, **kwargs):
        # Validation stricte du question_code : Q1 à Q21 uniquement
        question_code = request.data.get('question_code', '').strip().upper()
        if question_code:
            # Vérifier le format Q1-Q21
            import re
            if not re.match(r'^Q([1-9]|1[0-9]|2[01])$', question_code):
                return Response({
                    'success': False,
                    'error': f'Code question invalide : "{question_code}". Seuls les codes Q1 à Q21 sont autorisés.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Validation stricte du question_code : Q1 à Q21 uniquement
        question_code = request.data.get('question_code', '').strip().upper()
        if question_code:
            # Vérifier le format Q1-Q21
            import re
            if not re.match(r'^Q([1-9]|1[0-9]|2[01])$', question_code):
                return Response({
                    'success': False,
                    'error': f'Code question invalide : "{question_code}". Seuls les codes Q1 à Q21 sont autorisés.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)