from django.contrib import admin
from django.urls import path, include
from authentication import views
from django.http import JsonResponse

def test_view(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', test_view),
    path("authentication/", include("authentication.urls")),  # ✅ correct
    path("manager/login/", views.manager_login, name="manager_login"),
    path("manager/tests/<int:test_id>/generate-qr/", views.manager_generate_test_qr, name="manager_generate_test_qr"),
    path("hse/qr/decode/", views.decode_qr_and_prepare_test, name="decode_qr_and_prepare_test"),
    path("hse/test/<int:test_id>/start/", views.authenticate_hse_user_and_start_test, name="authenticate_hse_user_and_start_test"),
    path("hse/test/session/<int:test_session_id>/submit/", views.submit_test_answers, name="submit_test_answers"),
    path("user/current/", views.get_current_user, name="get_current_user"),
    path("logout/", views.logout_user, name="logout_user"),
]
