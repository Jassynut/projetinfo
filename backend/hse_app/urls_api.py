from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import HSEUserViewSet, HSEManagerViewSet

router = DefaultRouter()
router.register(r'users', HSEUserViewSet, basename='hse-user')
router.register(r'managers', HSEManagerViewSet, basename='hse-manager')

urlpatterns = [
    path('', include(router.urls)),
]
