from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import (
    TestViewSet,
    TestAttemptViewSet,
    user_test_attempts,
    list_versions,
    list_active_versions,
    version_questions,
    version_add_question,
    version_detail,
    verify_cni,
    test_questions_public,
    test_submit_answer,
    test_finish_public,
    test_result_public,
)
from .views_api_questions import QuestionViewSet

router = DefaultRouter()
router.register(r'', TestViewSet, basename='test-viewset')
router.register(r'attempts', TestAttemptViewSet, basename='test-attempt')
router.register(r'questions', QuestionViewSet, basename='question-viewset')

urlpatterns = [
    path('', include(router.urls)),
    path('my-attempts/', user_test_attempts, name='user-test-attempts'),
    # Alias "versions" pour compat frontend
    path('versions', list_versions, name='versions-list'),
    path('versions/actives', list_active_versions, name='versions-active'),
    path('versions/<int:pk>', version_detail, name='versions-detail'),
    path('versions/<int:pk>/questions', version_questions, name='versions-questions'),
    path('versions/<int:pk>/questions/add', version_add_question, name='versions-questions-add'),
    # Endpoints apprenant alignés maquette
    path('test/verifier-cni', verify_cni, name='verify-cni'),
    path('test/<int:test_id>/questions', test_questions_public, name='test-questions-public'),
    path('test/<int:test_id>/reponse', test_submit_answer, name='test-submit-answer'),
    path('test/<int:test_id>/terminer', test_finish_public, name='test-finish-public'),
    path('test/<int:test_id>/resultat', test_result_public, name='test-result-public'),
]
