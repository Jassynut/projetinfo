from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import TestViewSet, TestAttemptViewSet, user_test_attempts

router = DefaultRouter()
router.register(r'', TestViewSet, basename='test')
router.register(r'attempts', TestAttemptViewSet, basename='test-attempt')

urlpatterns = [
    path('', include(router.urls)),
    path('my-attempts/', user_test_attempts, name='user-test-attempts'),
]
