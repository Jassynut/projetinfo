from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from django.conf import settings
from django.conf.urls.static import static
from authentication import views
from tests.views_api import list_versions, list_active_versions, version_detail
from rest_framework.routers import DefaultRouter
from tests.views_api import QuestionViewSet
from hse_app import views as hse_views

# Fonction pour rediriger vers le front-end React
def redirect_to_front(request):
    return HttpResponseRedirect("http://localhost:5173/")   # 👉 Page Login React

questions_router = DefaultRouter(trailing_slash=False)
questions_router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Redirection principale vers la page Login React
    path('', redirect_to_front),

    # MODULE STATS (EXCEL, HSE)
    path('stats/', include('stats.urls')),

    # AUTHENTIFICATION API
    path('api/auth/', include('authentication.urls')),

    # HSE API (router DRF + endpoints simples)
    path('api/hse/', include('hse_app.urls_api')),
    # HSE API (autres endpoints dans views.py)
    path('api/hse/', include('hse_app.urls')),
    # Import Excel utilisateurs HSE (alias direct)
    path('api/users/import/', hse_views.import_hse_users, name='import_hse_users'),
    path('api/users/import/preview/', hse_views.preview_hse_users_excel, name='preview_hse_users_excel'),

    # ALIAS PUBLICS VERSIONS (contournent l'auth du ViewSet)
    path('api/versions', list_versions, name='api-versions-list'),
    path('api/versions/actives', list_active_versions, name='api-versions-actives'),
    path('api/versions/<int:pk>', version_detail, name='api-versions-detail'),

    # QUESTIONS API direct
    path('api/', include(questions_router.urls)),

    # CERTIFICATS API
    path('api/certificates/', include('certificats.urls_api')),
    # Alias FR
    path('api/certificats/', include('certificats.urls_api')),

    # ENDPOINTS DIRECTS (non API)
    path("manager/login/", views.manager_login, name="manager_login"),
    path("user/current/", views.get_current_user, name="get_current_user"),
    path("logout/", views.logout_user, name="logout_user"),
     path('api/', include('tests.urls_api')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
