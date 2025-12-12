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
        
        # Mettre à jour le score de l'utilisateur HSE si lié
        try:
            hse_user = HSEUser.objects.get(test_user=request.user)
            # Score = (pourcentage / 100) * 21
            hse_user.score = round((attempt.overall_score_percentage / 100) * 21)
            hse_user.reussite = attempt.passed
            hse_user.save()
        except HSEUser.DoesNotExist:
            pass
        
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
            return Response({'success': False, 'error': 'Version invalide'}, status=400)
        try:
            test = Test.objects.create(
                version=version,
                description=description,
                ordre_questions=[],
                mandatory_questions=[],
                total_questions=21,
                mandatory_questions_count=9,
                is_active=True,
            )
        except IntegrityError as exc:
            return Response({'success': False, 'error': str(exc)}, status=400)
        except Exception as exc:
            return Response({'success': False, 'error': str(exc)}, status=500)
        return Response(
            {
                'success': True,
                'version': {
                    'id': test.id,
                    'version': test.version,
                    'description': test.description,
                    'name': f"Version {test.version}",
                    'total_questions': test.total_questions,
                    'created_at': test.created_at,
                },
            },
            status=201,
        )

    qs = Test.objects.all().order_by('version')
    data = []
    for t in qs:
        item = TestListSerializer(t).data
        item['name'] = f"Version {t.version}"
        data.append(item)
    return Response({'versions': data})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def list_active_versions(request):
    qs = Test.objects.filter(is_active=True).order_by('version')
    serializer = TestListSerializer(qs, many=True)
    data = serializer.data
    # ajouter 'name' pour le frontend
    for item in data:
        item['name'] = f"Version {item.get('version')}"
    return Response({'versions': data})


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.AllowAny])
def version_detail(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.method == 'GET':
        data = TestDetailSerializer(test).data
        data['name'] = f"Version {test.version}"
        return Response(data)
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
    test.delete()
    return Response({'success': True})


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
    serializer = QuestionDetailSerializer(questions, many=True)
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
    test = get_object_or_404(Test, id=test_id)
    provided_answers = request.data.get('answers') or {}
    cache_key = f"test_answers:{request.session.session_key}:{test_id}"
    cached_answers = cache.get(cache_key, {})
    # merge (answers payload has priority)
    cached_answers.update(provided_answers)

    mandatory_correct = 0
    optional_correct = 0
    mandatory_ids = set(test.mandatory_questions or [])

    for qid_str, data in cached_answers.items():
        try:
            qid = int(qid_str)
            question = Question.objects.get(id=qid)
        except (ValueError, Question.DoesNotExist):
            continue
        user_answer = data.get('answer') if isinstance(data, dict) else data
        is_correct = question.check_answer(user_answer)
        if qid in mandatory_ids:
            if is_correct:
                mandatory_correct += 1
        else:
            if is_correct:
                optional_correct += 1

    total_score = mandatory_correct + optional_correct
    overall = total_score  # points = questions
    cache.set(f"test_result:{request.session.session_key}:{test_id}", {
        'score': overall,
        'mandatory_correct': mandatory_correct,
        'optional_correct': optional_correct,
        'test_version': test.version
    }, 60 * 30)
    cache.delete(cache_key)

    return Response({
        'success': True,
        'score': overall,
        'mandatory_correct': mandatory_correct,
        'optional_correct': optional_correct,
        'total_questions': test.total_questions,
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
        'attempt_id': None,
        'certificate_id': None,
    })


from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Question
from .serializers_api import QuestionDetailSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    """
    CRUD basique des questions pour compatibilité frontend
    """

    queryset = Question.objects.all().order_by('question_code')
    serializer_class = QuestionDetailSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
