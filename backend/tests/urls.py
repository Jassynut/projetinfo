# backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Authentication
    path('api/auth/', include('backend.authentication.urls')),
    
    # API HSE
    path('api/hse/', include('backend.hse_app.urls')),
    
    # API Tests généraux
    path('api/tests/', include('backend.tests.urls')),  # ← AJOUTE CETTE LIGNE
]