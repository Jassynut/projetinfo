# authentication/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentification de base
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('current-user/', views.current_user, name='current_user'),
    
    # Gestion du profil
    path('change-access-code/', views.change_access_code, name='change_access_code'),
    path('login-history/', views.login_history, name='login_history'),
    
    # Administration (staff seulement)
    path('admin/users/', views.admin_users_list, name='admin_users_list'),
    path('admin/create-user/', views.admin_create_user, name='admin_create_user'),
]