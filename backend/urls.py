from django.contrib import admin
from django.urls import path, include
from authentication import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Authentication
    path('api/auth/', include('authentication.urls')),
    
    # API HSE (REST Framework)
    path('api/hse/', include('hse_app.urls_api')),
    
    # API Tests (REST Framework)
    path('api/tests/', include('tests.urls_api')),
    
    # API Certificats (REST Framework)
    path('api/certificates/', include('certificats.urls_api')),
    
    # Authentication views
    path("authentication/", include("authentication.urls")),
    path("manager/login/", views.manager_login, name="manager_login"),
    path("user/current/", views.get_current_user, name="get_current_user"),
    path("logout/", views.logout_user, name="logout_user"),
]
