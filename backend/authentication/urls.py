# authentication/urls.py
from django.urls import path
from . import views
from .views import UploadApprenantsView

app_name = 'auth'

urlpatterns = [
    path('test/<int:test_id>/auth/', views.authenticate_hse_user_and_start_test, name='auth_start_test'),
    path('manager/generate-qr/<int:test_id>/', views.manager_generate_test_qr, name='manager_generate_qr'),
    path('decode-qr/', views.decode_qr_and_prepare_test, name='decode_qr'),
    path('current-user/', views.get_current_user, name='current_user'),
    path('logout/', views.logout_user, name='logout'),
]