from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from authentication import views

# Fonction pour rediriger vers le front-end React
def redirect_to_front(request):
    return HttpResponseRedirect("http://localhost:5173/")   # 👉 Page Login React

urlpatterns = [
    path('admin/', admin.site.urls),

    # Redirection principale vers la page Login React
    path('', redirect_to_front),

    # MODULE STATS (EXCEL, HSE)
    path('stats/', include('stats.urls')),

    # AUTHENTIFICATION API
    path('api/auth/', include('authentication.urls')),

    # HSE API
    path('api/hse/', include('hse_app.urls_api')),

    # TESTS API
    path('api/tests/', include('tests.urls_api')),
    # Alias compat frontend
    path('api/versions/', include('tests.urls_api')),
    path('api/questions/', include('tests.urls_api')),
    path('api/test/', include('tests.urls_api')),

    # CERTIFICATS API
    path('api/certificates/', include('certificats.urls_api')),
    # Alias FR
    path('api/certificats/', include('certificats.urls_api')),

    # ENDPOINTS DIRECTS (non API)
    path("manager/login/", views.manager_login, name="manager_login"),
    path("user/current/", views.get_current_user, name="get_current_user"),
    path("logout/", views.logout_user, name="logout_user"),
]
