from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import HSEUserViewSet, HSEManagerViewSet, upload_excel
from . import views

router = DefaultRouter()
router.register(r'users', HSEUserViewSet, basename='hse-user')
router.register(r'managers', HSEManagerViewSet, basename='hse-manager')

urlpatterns = [
    # Endpoints simples AVANT le router pour éviter les conflits
    path('users/list/', views.list_hse_users, name='list_hse_users_simple'),
    path('users/search/', views.search_hse_user_by_cin, name='search_hse_user'),
    path('upload_excel/', upload_excel, name='upload_excel'),
    # Router DRF (doit être en dernier)
    path('', include(router.urls)),
]
