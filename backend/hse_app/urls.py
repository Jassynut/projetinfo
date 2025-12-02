# hse_app/urls.py - CORRIGÉ
from django.urls import path
from . import views

urlpatterns = [
    # Users HSE
    path('users/search/', views.search_hse_user_by_cin, name='search_hse_user'),
    path('users/create/', views.create_hse_user, name='create_hse_user'),
    path('users/', views.list_hse_users, name='list_hse_users'),
    
    # Tests HSE
    path('tests/', views.list_hse_tests, name='list_hse_tests'),
    path('tests/version/<int:version>/', views.get_hse_test_details, name='test_details'),  # ← CHANGÉ ICI
    
    # Test Attempts
    path('test-attempts/start/', views.start_hse_test_attempt, name='start_test_attempt'),
    path('test-attempts/<int:attempt_id>/submit/', views.submit_hse_test_answers, name='submit_test_answers'),
    path('test-attempts/history/', views.get_user_test_history, name='test_history'),
    
    # Statistics
    path('statistics/', views.get_hse_statistics, name='hse_statistics'),
    
    # Managers
    path('managers/', views.list_hse_managers, name='list_managers'),
    path('managers/create/', views.create_hse_manager, name='create_manager'),
    
    # Sync
    path('sync-users/', views.sync_test_users_with_hse, name='sync_users'),
]