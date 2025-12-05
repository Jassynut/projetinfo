# backend/urls.py
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from authentication import views


def test_view(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', test_view),  # Pas d'include du tout,
    # 📌 AUTHENTIFICATION MANAGER
    # ============================
    path("manager/login/", views.manager_login, name="manager_login"),

    # ======================================
    # 📌 MANAGER - GENERER QR POUR UN TEST
    # Exemple: /api/manager/tests/5/generate-qr/
    # ======================================
    path(
        "manager/tests/<int:test_id>/generate-qr/",
        views.manager_generate_test_qr,
        name="manager_generate_test_qr"
    ),

    # ======================================
    # 📌 UTILISATEUR HSE (MOBILE)
    # Décodage du QR après scan
    # ======================================
    path(
        "hse/qr/decode/",
        views.decode_qr_and_prepare_test,
        name="decode_qr_and_prepare_test"
    ),

    # =========================================
    # 📌 AUTH UTILISATEUR HSE PAR CIN
    # Exemple: /hse/test/5/start/
    # =========================================
    path(
        "hse/test/<int:test_id>/start/",
        views.authenticate_hse_user_and_start_test,
        name="authenticate_hse_user_and_start_test"
    ),

    # =========================================
    # 📌 SOUMISSION DU TEST
    # Exemple: /hse/test/session/12/submit/
    # =========================================
    path(
        "hse/test/session/<int:test_session_id>/submit/",
        views.submit_test_answers,
        name="submit_test_answers"
    ),

    # =========================
    # 📌 UTILITAIRES
    # =========================
    path(
        "user/current/",
        views.get_current_user,
        name="get_current_user"
    ),

    path(
        "logout/",
        views.logout_user,
        name="logout_user"
    ),
]
